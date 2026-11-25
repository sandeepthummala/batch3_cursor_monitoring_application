function formatBytesPair(used, total) {
  if (used == null || total == null) return "";
  return `(${used} / ${total} B)`;
}

async function fetchJson(url) {
  const res = await fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } });
  if (res.status === 401 || res.redirected) {
    window.location.href = "/login";
    return null;
  }
  if (!res.ok) throw new Error("refresh failed");
  return res.json();
}

function initDashboardRefresh(intervalMs) {
  const root = document.getElementById("dashboard-cards");
  if (!root) return;

  async function tick() {
    try {
      const data = await fetchJson("/api/dashboard/metrics");
      if (!data) return;
      for (const item of data.servers) {
        const col = root.querySelector(`[data-server-id="${item.server_id}"]`);
        if (!col) continue;
        const badge = col.querySelector(".status-badge");
        const summary = col.querySelector(".metrics-summary");
        if (item.reachable) {
          badge.className = "badge status-badge text-bg-success";
          badge.textContent = "reachable";
          summary.innerHTML =
            `<div>CPU: <strong class="cpu">${item.cpu_percent}%</strong></div>` +
            `<div>Memory: <strong class="mem">${item.memory_percent}%</strong> ` +
            `<span class="text-secondary small mem-detail">${formatBytesPair(item.memory_used, item.memory_total)}</span></div>`;
        } else {
          badge.className = "badge status-badge text-bg-danger";
          badge.textContent = "unreachable";
          summary.innerHTML = `<div class="text-danger small error-msg"></div>`;
          summary.querySelector(".error-msg").textContent = item.error || "unreachable";
        }
      }
    } catch (e) {
      // Keep last rendered values on transient errors
    }
  }

  setInterval(tick, intervalMs);
}

function initDetailRefresh(intervalMs) {
  const root = document.getElementById("detail-metrics");
  if (!root) return;
  const serverId = root.dataset.serverId;

  async function tick() {
    try {
      const item = await fetchJson(`/api/servers/${serverId}/metrics`);
      if (!item) return;
      const badge = root.querySelector(".status-badge");
      const err = root.querySelector(".error-msg");
      const block = root.querySelector(".reachable-block");
      if (item.reachable) {
        badge.className = "badge status-badge text-bg-success";
        badge.textContent = "reachable";
        if (err) err.textContent = "";
        if (block) block.classList.remove("d-none");
        const cpu = root.querySelector(".cpu");
        const mem = root.querySelector(".mem");
        const memDetail = root.querySelector(".mem-detail");
        if (cpu) cpu.textContent = `${item.cpu_percent ?? "—"}%`;
        if (mem) mem.textContent = `${item.memory_percent ?? "—"}%`;
        if (memDetail) memDetail.textContent = formatBytesPair(item.memory_used, item.memory_total);

        const netBody = root.querySelector(".net-body");
        if (netBody) {
          netBody.innerHTML = "";
          if (!item.network.length) {
            netBody.innerHTML = `<tr><td colspan="3" class="text-secondary">No interfaces</td></tr>`;
          } else {
            for (const n of item.network) {
              const tr = document.createElement("tr");
              tr.innerHTML = `<td></td><td></td><td></td>`;
              tr.children[0].textContent = n.interface;
              tr.children[1].textContent = n.rx_bytes;
              tr.children[2].textContent = n.tx_bytes;
              netBody.appendChild(tr);
            }
          }
        }

        const portsBody = root.querySelector(".ports-body");
        if (portsBody) {
          portsBody.innerHTML = "";
          if (!item.ports.length) {
            portsBody.innerHTML = `<tr><td colspan="3" class="text-secondary">No ports</td></tr>`;
          } else {
            for (const p of item.ports) {
              const tr = document.createElement("tr");
              tr.innerHTML = `<td></td><td></td><td class="small"></td>`;
              tr.children[0].textContent = p.state;
              tr.children[1].textContent = p.local;
              tr.children[2].textContent = p.process || "";
              portsBody.appendChild(tr);
            }
          }
        }
      } else {
        badge.className = "badge status-badge text-bg-danger";
        badge.textContent = "unreachable";
        if (err) err.textContent = item.error || "unreachable";
        if (block) block.classList.add("d-none");
      }
    } catch (e) {
      // keep last values
    }
  }

  setInterval(tick, intervalMs);
}
