import pytest
from rest_framework.test import APIClient

from .models import APIKey, Client


@pytest.mark.django_db
def test_api_key_authenticates_active_client():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().get("/api/v1/health/", HTTP_API_KEY=raw_key)
    assert response.status_code == 200


@pytest.mark.django_db
def test_invalid_api_key_is_rejected_on_protected_view():
    client = Client.objects.create(name="Demo fintech")
    APIKey.issue(client)
    response = APIClient().get("/api/v1/client/", HTTP_API_KEY="wrong")
    assert response.status_code == 401


@pytest.mark.django_db
def test_protected_view_returns_authenticated_client():
    client = Client.objects.create(name="Demo fintech")
    _, raw_key = APIKey.issue(client)
    response = APIClient().get("/api/v1/client/", HTTP_API_KEY=raw_key)
    assert response.status_code == 200
    assert response.json()["client_id"] == client.client_id
