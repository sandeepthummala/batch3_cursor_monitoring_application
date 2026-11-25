from tests.conftest import login


def test_login_success(client, admin_creds):
    resp = login(client, admin_creds["username"], admin_creds["password"])
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


def test_login_failure_wrong_password(client, admin_creds):
    resp = login(client, admin_creds["username"], "wrong-password")
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data


def test_protected_route_redirects_when_logged_out(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_logout_clears_access(client, admin_creds):
    login(client, admin_creds["username"], admin_creds["password"])
    assert client.get("/").status_code == 200
    resp = client.post("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
    assert client.get("/").status_code == 302
