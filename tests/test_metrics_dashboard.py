from unittest.mock import patch

from app.crypto_util import encrypt_secret
from app.extensions import db
from app.models import Server
from app.ssh import MetricsResult
from tests.conftest import login


SAMPLE = MetricsResult(
    reachable=True,
    cpu_percent=12.5,
    memory_used=100,
    memory_total=200,
    memory_percent=50.0,
    network=[{"interface": "eth0", "rx_bytes": 1, "tx_bytes": 2}],
    ports=[{"state": "LISTEN", "local": "0.0.0.0:22", "port": "22", "process": ""}],
)


def _seed(app):
    with app.app_context():
        server = Server(
            display_name="node1",
            host="10.0.0.5",
            ssh_username="ubuntu",
            auth_method="password",
            ssh_password_encrypted=encrypt_secret("super-secret-pass"),
            ssh_port=22,
        )
        db.session.add(server)
        db.session.commit()
        return server.id


def test_dashboard_and_detail_require_auth(client):
    assert client.get("/").status_code == 302
    assert client.get("/servers/1").status_code == 302
    assert client.get("/api/dashboard/metrics").status_code == 302
    assert client.get("/api/servers/1/metrics").status_code == 302


def test_dashboard_detail_with_mocked_metrics(client, app, admin_creds):
    login(client, admin_creds["username"], admin_creds["password"])
    sid = _seed(app)
    with patch("app.routes.main.collect_metrics", return_value=SAMPLE):
        dash = client.get("/")
        detail = client.get(f"/servers/{sid}")
    assert dash.status_code == 200
    assert b"node1" in dash.data
    assert b"12.5" in dash.data
    assert detail.status_code == 200
    assert b"Listening ports" in detail.data
    assert b"super-secret-pass" not in detail.data


def test_metrics_api_rejects_anonymous_and_returns_json(client, app, admin_creds):
    sid = _seed(app)
    assert client.get(f"/api/servers/{sid}/metrics").status_code == 302

    login(client, admin_creds["username"], admin_creds["password"])
    with patch("app.routes.api.collect_metrics", return_value=SAMPLE):
        resp = client.get(f"/api/servers/{sid}/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["reachable"] is True
    assert "ssh_password" not in data
    assert data["cpu_percent"] == 12.5
