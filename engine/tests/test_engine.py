# For: Unit and integration tests covering pipeline, rules, and API endpoints
# Must never: Leave test temporary databases or files uncleaned

import pytest
from fastapi.testclient import TestClient
from engine.app.main import app
from engine.app.rules.validation import compare_names, compare_percentages, compare_dates
from engine.app.rules.eligibility import evaluate_application_eligibility


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_name_matching():
    """Verifies fuzzy name comparison with token-set ratio."""
    status, ratio, _ = compare_names("RAHUL K SHARMA", "Rahul Kumar Sharma")
    assert status == "match"
    assert ratio >= 0.90

    status_diff, _, _ = compare_names("Amit Kumar Verma", "Rahul Sharma")
    assert status_diff == "mismatch"


def test_percentage_matching():
    """Verifies numeric tolerance of 0.01 for percentage rounding."""
    status, _ = compare_percentages("74.20", "74.205", tolerance=0.01)
    assert status == "match"

    status_mismatch, reason = compare_percentages("72.4", "74.2", tolerance=0.01)
    assert status_mismatch == "mismatch"
    assert "Differs by 1.8" in reason or "1.8" in reason


def test_date_matching():
    """Verifies ISO normalization of several common date formats."""
    status, _ = compare_dates("14/05/1999", "1999-05-14")
    assert status == "match"


def test_eligibility_evaluation():
    """Verifies vacancy eligibility rule engine."""
    biodata = {
        "dob": "1999-05-14",
        "category": "OBC",
        "qualification": {"branch": "ECE", "percentage": 74.2},
        "gate": {"year": 2023, "score": 612}
    }
    rules = {
        "min_percentage": 60.0,
        "allowed_branches": ["ECE", "EEE"],
        "gate_required": True,
        "gate_validity_years": 3,
        "max_age": {"UR": 28, "OBC": 31, "SC": 33, "ST": 33, "PwD_extra": 10}
    }
    result = evaluate_application_eligibility(biodata, rules, "2024-12-31")
    assert result["verdict"] == "eligible"


def test_api_health(client):
    """Verifies engine health and audit integrity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["audit_integrity"] is True


def test_auth_login(client):
    """Verifies authentication and JWT issuance."""
    response = client.post("/auth/login", json={"username": "officer1", "password": "Officer@123"})
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["user"]["role"] == "officer"


def test_preset_instant_verification(client):
    """Verifies 1-click sample preset instant verification."""
    auth_resp = client.post("/auth/login", json={"username": "officer1", "password": "Officer@123"})
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test clean preset
    clean_resp = client.post("/verify/preset/clean", headers=headers)
    assert clean_resp.status_code == 200
    assert clean_resp.json()["processing_ms"] <= 3000

    # Test blurry scan quality gate rejection (422 UNREADABLE_DOCUMENT)
    blurry_resp = client.post("/verify/preset/blurry", headers=headers)
    assert blurry_resp.status_code == 422

