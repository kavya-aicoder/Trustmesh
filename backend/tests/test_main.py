from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "TrustLayer API Gateway",
        "status": "online",
        "version": "0.1.0",
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_auth_status():
    response = client.get("/auth/status")

    assert response.status_code == 200
    assert response.json()["service"] == "authentication"
    assert response.json()["status"] == "ready"


def test_access_check():
    response = client.post(
        "/access/check",
        json={
            "org_id": "demo-org",
            "did": "did:example:alice",
            "resource_id": "document-1",
            "action": "read",
        },
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False


def test_assets():
    response = client.get("/assets/")

    assert response.status_code == 200
    assert response.json()["count"] == 4
    assert len(response.json()["assets"]) == 4
    assert response.json()["assets"][0]["asset_id"] == "asset-001"


def test_audit():
    from app.indexer.service import event_repository

    event_repository.clear()

    response = client.get("/audit/")

    assert response.status_code == 200
    assert response.json()["events"] == []


def test_siwe_message():
    response = client.post(
        "/auth/siwe/message",
        json={
            "domain": "localhost:8000",
            "address": "0x1234567890123456789012345678901234567890",
            "statement": "Sign in to TrustLayer.",
            "uri": "http://localhost:8000",
            "chain_id": 80002,
            "nonce": "abc12345",
            "issued_at": "2026-09-10T06:00:00Z",
        },
    )

    assert response.status_code == 200

    message = response.json()["message"]

    assert "localhost:8000 wants you to sign in" in message
    assert "0x1234567890123456789012345678901234567890" in message
    assert "Chain ID: 80002" in message
    assert "Nonce: abc12345" in message


def test_siwe_message_rejects_invalid_address():
    response = client.post(
        "/auth/siwe/message",
        json={
            "domain": "localhost:8000",
            "address": "invalid",
            "statement": "Sign in to TrustLayer.",
            "uri": "http://localhost:8000",
            "chain_id": 80002,
            "nonce": "abc12345",
            "issued_at": "2026-09-10T06:00:00Z",
        },
    )

    assert response.status_code == 422


def test_siwe_nonce():
    response = client.post("/auth/siwe/nonce")

    assert response.status_code == 200

    nonce = response.json()["nonce"]

    assert isinstance(nonce, str)
    assert len(nonce) >= 8


def test_siwe_verify_rejects_invalid_nonce():
    response = client.post(
        "/auth/siwe/verify",
        json={
            "message": "test message",
            "signature": "0xinvalid",
            "address": "0x1234567890123456789012345678901234567890",
            "nonce": "invalidnonce",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or already-used nonce"