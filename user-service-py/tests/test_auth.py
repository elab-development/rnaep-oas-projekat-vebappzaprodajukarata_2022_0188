"""
Testovi za autentifikaciju, profil i password reset.
Pokreni sa:  pytest
"""


def login_token(client, email, password):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.json()["token"]


# ---------- Registracija ----------

def test_user_can_register(client):
    resp = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!",
        "password_confirmation": "Password123!",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "test@example.com"


def test_user_cannot_register_with_existing_email(client, make_user):
    make_user(email="test@example.com")
    resp = client.post("/api/auth/register", json={
        "name": "Another",
        "email": "test@example.com",
        "password": "Password123!",
        "password_confirmation": "Password123!",
    })
    assert resp.status_code == 422
    assert "već registrovana" in resp.json()["detail"]


def test_register_password_mismatch(client):
    resp = client.post("/api/auth/register", json={
        "name": "Test",
        "email": "x@example.com",
        "password": "Password123!",
        "password_confirmation": "Drugacija123!",
    })
    assert resp.status_code == 422


# ---------- Login ----------

def test_user_can_login(client, make_user):
    make_user(email="test@example.com", password="Password123!")
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "Password123!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"


def test_login_wrong_password(client, make_user):
    make_user(email="test@example.com", password="Password123!")
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "PogresnaLozinka!",
    })
    assert resp.status_code == 401


# ---------- Profil / zaštićene rute ----------

def test_me_returns_current_user(client, make_user):
    make_user(email="test@example.com", password="Password123!")
    token = login_token(client, "test@example.com", "Password123!")
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_unauthenticated_cannot_access_me(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_user_can_logout(client, make_user):
    make_user(email="test@example.com", password="Password123!")
    token = login_token(client, "test@example.com", "Password123!")
    resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


# ---------- Password reset ----------

def test_user_can_request_password_reset(client, make_user):
    make_user(email="test@example.com")
    resp = client.post("/api/auth/forgot-password", json={"email": "test@example.com"})
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_cannot_request_reset_for_unknown_email(client):
    resp = client.post("/api/auth/forgot-password", json={"email": "nepostoji@example.com"})
    assert resp.status_code == 422


def test_can_validate_reset_token(client, make_user):
    make_user(email="test@example.com")
    token = client.post("/api/auth/forgot-password",
                        json={"email": "test@example.com"}).json()["token"]
    resp = client.post("/api/auth/validate-reset-token", json={"token": token})
    assert resp.status_code == 200


def test_invalid_reset_token_rejected(client):
    resp = client.post("/api/auth/validate-reset-token", json={"token": "nepostojeci"})
    assert resp.status_code == 422


def test_user_can_reset_password(client, make_user):
    make_user(email="test@example.com", password="StaraLozinka1!")
    token = client.post("/api/auth/forgot-password",
                        json={"email": "test@example.com"}).json()["token"]
    resp = client.post("/api/auth/reset-password", json={
        "token": token,
        "password": "NovaLozinka123!",
        "password_confirmation": "NovaLozinka123!",
    })
    assert resp.status_code == 200
    # Provera da nova lozinka radi
    login = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "NovaLozinka123!",
    })
    assert login.status_code == 200


def test_reset_password_too_short(client, make_user):
    make_user(email="test@example.com")
    token = client.post("/api/auth/forgot-password",
                        json={"email": "test@example.com"}).json()["token"]
    resp = client.post("/api/auth/reset-password", json={
        "token": token,
        "password": "kratka",
        "password_confirmation": "kratka",
    })
    assert resp.status_code == 422


# ---------- Admin / role-based ----------

def test_admin_can_list_users(client, make_user):
    make_user(email="admin@example.com", password="Admin123!", role="admin")
    token = login_token(client, "admin@example.com", "Admin123!")
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_regular_user_cannot_list_users(client, make_user):
    make_user(email="user@example.com", password="User123!", role="user")
    token = login_token(client, "user@example.com", "User123!")
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


# ---------- Health ----------

def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
