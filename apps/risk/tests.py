import pytest
from rest_framework.test import APIClient

from apps.clients.models import APIKey, Client


@pytest.mark.django_db
def test_risk_assessment_fuses_selected_modules():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/risk-assessment/", {
        "transaction_id": "tx_1", "user_token": "usr_1", "amount": "250000", "currency": "NGN",
        "enabled_modules": ["behavioral", "environment"], "module_scores": {"behavioral": 80, "environment": 70},
    }, format="json", HTTP_API_KEY=raw_key)
    assert response.status_code == 201
    assert response.json()["risk_score"] == 76
    assert response.json()["decision"] == "HOLD"


@pytest.mark.django_db
def test_risk_assessment_rejects_zero_amount():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/risk-assessment/", {
        "transaction_id": "tx_1", "user_token": "usr_1", "amount": "0", "currency": "NGN",
        "enabled_modules": ["behavioral"],
    }, format="json", HTTP_API_KEY=raw_key)
    assert response.status_code == 400


@pytest.mark.django_db
def test_transaction_risk_uses_personalized_baseline_and_recipient_signals():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/transaction-risk/", {
        "transaction_id": "tx_behavioral", "user_token": "usr_1", "amount": "250000", "currency": "NGN",
        "recipient": {"is_new": True, "verification_level": "LOW"},
        "sender_profile": {"average_transaction_amount": 10000, "maximum_transaction_amount": 50000},
    }, format="json", HTTP_API_KEY=raw_key)
    body = response.json()
    assert response.status_code == 201
    assert body["risk_score"] == 100
    assert {signal["code"] for signal in body["signals"]} == {
        "AMOUNT_ANOMALY", "NEW_RECIPIENT", "LOW_RECIPIENT_VERIFICATION"
    }


@pytest.mark.django_db
def test_recipient_risk_is_independently_callable():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/recipient-risk/", {
        "transaction_id": "tx_recipient", "user_token": "usr_1", "recipient_token": "rcp_1",
        "recipient": {"is_new": True, "verification_level": "LOW", "account_age_days": 14},
    }, format="json", HTTP_API_KEY=raw_key)
    body = response.json()
    assert response.status_code == 201
    assert body["risk_score"] == 90
    assert body["risk_level"] == "CRITICAL"


@pytest.mark.django_db
def test_environment_risk_normalizes_supplied_security_signals():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/environment-risk/", {
        "transaction_id": "tx_environment", "user_token": "usr_1",
        "device": {"is_new": True}, "network": {"new_ip": True}, "location": {"is_new": True},
        "telecom": {"recent_sim_swap": True}, "account_security": {"new_beneficiary": True},
    }, format="json", HTTP_API_KEY=raw_key)
    body = response.json()
    assert response.status_code == 201
    assert body["risk_score"] == 100
    assert "RECENT_SIM_SWAP" in {signal["code"] for signal in body["signals"]}


@pytest.mark.django_db
def test_facial_risk_returns_derived_distress_signal_without_raw_image():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/facial-risk/", {
        "transaction_id": "tx_facial", "user_token": "usr_1", "identity_verified": True,
        "ml_result": {"neutral": 0.1, "sad": 0.2, "angry": 0.15, "fear": 0.53},
    }, format="json", HTTP_API_KEY=raw_key)
    body = response.json()
    assert response.status_code == 201
    assert body["risk_score"] == 88
    assert body["signals"][0]["code"] == "FACIAL_DISTRESS_SIGNAL"
    assert "image" not in body


@pytest.mark.django_db
def test_unified_assessment_is_idempotent():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    payload = {"transaction_id": "tx_repeat", "user_token": "usr_1", "amount": "10000", "currency": "NGN",
               "enabled_modules": ["behavioral"], "module_scores": {"behavioral": 10}}
    api = APIClient()
    first = api.post("/api/v1/risk-assessment/", payload, format="json", HTTP_API_KEY=raw_key, HTTP_IDEMPOTENCY_KEY="same-request")
    second = api.post("/api/v1/risk-assessment/", payload, format="json", HTTP_API_KEY=raw_key, HTTP_IDEMPOTENCY_KEY="same-request")
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.django_db
def test_unified_assessment_explains_transaction_status():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().post("/api/v1/risk-assessment/", {
        "transaction_id": "tx_explanation", "user_token": "usr_1", "amount": "10000", "currency": "NGN",
        "enabled_modules": ["behavioral"], "module_scores": {"behavioral": 10},
    }, format="json", HTTP_API_KEY=raw_key)
    assert response.json()["transaction_status"] == "SUCCESSFUL"
    assert response.json()["explanation"] == ["no material anomaly detected"]
