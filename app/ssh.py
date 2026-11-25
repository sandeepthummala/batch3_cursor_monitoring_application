"""SSH helpers: connection test and read-only metric collection (fixed commands)."""

from __future__ import annotations

import re
import socket
from dataclasses import dataclass, field
from typing import Any

import paramiko

from app.crypto_util import decrypt_secret
from app.models import Server

# Fixed remote commands only — never interpolate user input into the shell.
CMD_CPU = "grep 'cpu ' /proc/stat"
CMD_MEM = "free -b"
CMD_NET = "cat /proc/net/dev"
CMD_PORTS = "ss -tulnp 2>/dev/null || ss -tuln"


@dataclass
class SSHResult:
    ok: bool
    message: str


@dataclass
class MetricsResult:
    reachable: bool
    error: str | None = None
    cpu_percent: float | None = None
    memory_used: int | None = None
    memory_total: int | None = None
    memory_percent: float | None = None
    network: list[dict[str, Any]] = field(default_factory=list)
    ports: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reachable": self.reachable,
            "error": self.error,
            "cpu_percent": self.cpu_percent,
            "memory_used": self.memory_used,
            "memory_total": self.memory_total,
            "memory_percent": self.memory_percent,
            "network": self.network,
            "ports": self.ports,
        }


def _sanitize_error(exc: BaseException) -> str:
    text = str(exc)
    # Avoid leaking paths/secrets from verbose library messages in UI
    if "Authentication" in text or "auth" in text.lower():
        return "SSH authentication failed"
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "SSH connection timed out"
    if isinstance(exc, (socket.error, OSError)):
        return "SSH connection failed (host unreachable or refused)"
    return "SSH connection failed"


def _connect(server: Server, timeout: int) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    # Demo policy: AutoAddPolicy — document risk in SECURITY.md
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    kwargs: dict[str, Any] = {
        "hostname": server.host,
        "port": server.ssh_port or 22,
        "username": server.ssh_username,
        "timeout": timeout,
        "allow_agent": False,
        "look_for_keys": False,
    }

    if server.auth_method == "key":
        if not server.ssh_key_path:
            raise ValueError("SSH key path is not configured")
        kwargs["key_filename"] = server.ssh_key_path
    else:
        password = decrypt_secret(server.ssh_password_encrypted)
        if not password:
            raise ValueError("SSH password is not configured")
        kwargs["password"] = password

    client.connect(**kwargs)
    return client


def _run(client: paramiko.SSHClient, command: str, timeout: int) -> str:
    _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if code != 0 and not out.strip():
        raise RuntimeError(err.strip() or f"Command failed with exit {code}")
    return out


def check_ssh_connection(server: Server, timeout: int = 8) -> SSHResult:
    client = None
    try:
        client = _connect(server, timeout=timeout)
        _run(client, "echo ok", timeout=timeout)
        return SSHResult(ok=True, message="Connection successful")
    except Exception as exc:  # noqa: BLE001 — surface sanitized status to UI
        return SSHResult(ok=False, message=_sanitize_error(exc))
    finally:
        if client:
            client.close()


def parse_cpu(stat_line: str) -> float | None:
    # /proc/stat: cpu  user nice system idle iowait irq softirq ...
    parts = stat_line.split()
    if len(parts) < 5 or parts[0] != "cpu":
        return None
    values = [int(x) for x in parts[1:]]
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    total = sum(values)
    if total <= 0:
        return None
    return round(100.0 * (1.0 - idle / total), 1)


def parse_memory(free_output: str) -> tuple[int | None, int | None, float | None]:
    for line in free_output.splitlines():
        if line.startswith("Mem:"):
            cols = line.split()
            if len(cols) >= 3:
                total = int(cols[1])
                used = int(cols[2])
                pct = round(100.0 * used / total, 1) if total else None
                return used, total, pct
    return None, None, None


def parse_network(dev_output: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    lines = dev_output.strip().splitlines()
    for line in lines[2:]:
        if ":" not in line:
            continue
        iface, rest = line.split(":", 1)
        cols = rest.split()
        if len(cols) < 16:
            continue
        name = iface.strip()
        if name == "lo":
            continue
        rows.append(
            {
                "interface": name,
                "rx_bytes": int(cols[0]),
                "tx_bytes": int(cols[8]),
            }
        )
    return rows


def parse_ports(ss_output: str) -> list[dict[str, str]]:
    """Parse `ss -tulnp` output. Columns: Netid State Recv-Q Send-Q Local Peer ..."""
    ports: list[dict[str, str]] = []
    for line in ss_output.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 5:
            continue
        state = parts[1] if parts[0] in {"tcp", "udp", "tcp6", "udp6"} else parts[0]
        local = parts[4]
        process = ""
        if "users:" in line:
            process = line[line.index("users:") :].strip()
        m = re.search(r":(\d+)$", local)
        port = m.group(1) if m else local
        ports.append(
            {
                "state": state,
                "local": local,
                "port": port,
                "process": process,
            }
        )
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for p in ports:
        key = p["local"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique[:100]


def collect_metrics(
    server: Server, connect_timeout: int = 8, command_timeout: int = 10
) -> MetricsResult:
    client = None
    try:
        client = _connect(server, timeout=connect_timeout)
        cpu_out = _run(client, CMD_CPU, timeout=command_timeout)
        mem_out = _run(client, CMD_MEM, timeout=command_timeout)
        net_out = _run(client, CMD_NET, timeout=command_timeout)
        ports_out = _run(client, CMD_PORTS, timeout=command_timeout)

        used, total, mem_pct = parse_memory(mem_out)
        return MetricsResult(
            reachable=True,
            cpu_percent=parse_cpu(cpu_out.splitlines()[0] if cpu_out else ""),
            memory_used=used,
            memory_total=total,
            memory_percent=mem_pct,
            network=parse_network(net_out),
            ports=parse_ports(ports_out),
        )
    except Exception as exc:  # noqa: BLE001
        return MetricsResult(reachable=False, error=_sanitize_error(exc))
    finally:
        if client:
            client.close()
