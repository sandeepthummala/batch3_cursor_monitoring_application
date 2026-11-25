from unittest.mock import MagicMock, patch

from app.crypto_util import encrypt_secret
from app.extensions import db
from app.models import Server
from app.ssh import (
    SSHResult,
    check_ssh_connection,
    collect_metrics,
    parse_cpu,
    parse_memory,
)
from tests.conftest import login


def test_parse_cpu_and_memory():
    cpu = parse_cpu("cpu  100 0 100 800 0 0 0 0")
    assert cpu == 20.0
    used, total, pct = parse_memory("Mem: 1000 400 600 0 0 0\n")
    assert used == 400 and total == 1000 and pct == 40.0


def test_check_ssh_connection_mocked(app):
    with app.app_context():
        server = Server(
            display_name="t",
            host="example.local",
            ssh_username="u",
            auth_method="password",
            ssh_password_encrypted=encrypt_secret("p"),
            ssh_port=22,
        )
        with patch("app.ssh._connect") as connect:
            client = MagicMock()
            connect.return_value = client
            with patch("app.ssh._run", return_value="ok"):
                result = check_ssh_connection(server)
        assert isinstance(result, SSHResult)
        assert result.ok is True


def test_collect_metrics_unreachable(app):
    with app.app_context():
        server = Server(
            display_name="t",
            host="example.local",
            ssh_username="u",
            auth_method="password",
            ssh_password_encrypted=encrypt_secret("p"),
            ssh_port=22,
        )
        with patch("app.ssh._connect", side_effect=OSError("refused")):
            metrics = collect_metrics(server)
        assert metrics.reachable is False
        assert metrics.error
        assert "p" not in metrics.error


def test_test_button_auth_required(client):
    assert client.post("/servers/1/test").status_code == 302


def test_test_button_uses_mock(client, app, admin_creds):
    login(client, admin_creds["username"], admin_creds["password"])
    with app.app_context():
        server = Server(
            display_name="t",
            host="example.local",
            ssh_username="u",
            auth_method="password",
            ssh_password_encrypted=encrypt_secret("p"),
            ssh_port=22,
        )
        db.session.add(server)
        db.session.commit()
        sid = server.id

    with patch(
        "app.routes.servers.check_ssh_connection",
        return_value=SSHResult(True, "Connection successful"),
    ):
        resp = client.post(f"/servers/{sid}/test", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Connection successful" in resp.data
