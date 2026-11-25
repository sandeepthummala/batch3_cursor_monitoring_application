from app.crypto_util import encrypt_secret
from app.extensions import db
from app.models import Server
from tests.conftest import login


def _create_server(app, **overrides):
    with app.app_context():
        data = {
            "display_name": "web1",
            "host": "10.0.0.1",
            "ssh_username": "ubuntu",
            "auth_method": "password",
            "ssh_password_encrypted": encrypt_secret("secret"),
            "ssh_port": 22,
        }
        data.update(overrides)
        server = Server(**data)
        db.session.add(server)
        db.session.commit()
        return server.id


def test_unauthenticated_cannot_mutate_servers(client):
    assert client.get("/servers/").status_code == 302
    assert client.get("/servers/add").status_code == 302
    assert client.post("/servers/add", data={}).status_code == 302


def test_create_edit_delete_server(client, app, admin_creds):
    login(client, admin_creds["username"], admin_creds["password"])

    resp = client.post(
        "/servers/add",
        data={
            "display_name": "app1",
            "host": "192.168.1.10",
            "ssh_username": "monitor",
            "auth_method": "password",
            "ssh_password": "s3cret",
            "ssh_port": 22,
            "submit": "Save",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"app1" in resp.data
    assert b"s3cret" not in resp.data

    with app.app_context():
        server = Server.query.filter_by(display_name="app1").one()
        server_id = server.id
        assert server.ssh_password_encrypted
        assert "s3cret" not in (server.ssh_password_encrypted or "")

    resp = client.post(
        f"/servers/{server_id}/edit",
        data={
            "display_name": "app1-renamed",
            "host": "192.168.1.10",
            "ssh_username": "monitor",
            "auth_method": "password",
            "ssh_password": "",
            "ssh_port": 2222,
            "submit": "Save",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"app1-renamed" in resp.data
    assert b"2222" in resp.data

    list_html = client.get("/servers/").data
    assert b"s3cret" not in list_html

    resp = client.post(
        f"/servers/{server_id}/delete",
        data={"submit": "Delete"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"app1-renamed" not in resp.data


def test_list_does_not_show_passwords(client, app, admin_creds):
    login(client, admin_creds["username"], admin_creds["password"])
    _create_server(app)
    html = client.get("/servers/").data
    assert b"secret" not in html
    assert b"ssh_password" not in html
