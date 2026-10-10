from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    keyword = "Api-Key"

    def authenticate(self, request):
        supplied = request.headers.get(self.keyword)
        if not supplied:
            return None
        key = APIKey.objects.select_related("client").filter(
            key_hash=APIKey.digest(supplied), is_active=True, client__is_active=True
        ).first()
        if not key:
            raise AuthenticationFailed("Invalid API key")
        APIKey.objects.filter(pk=key.pk).update(last_used_at=timezone.now())
        return key.client, key

    def authenticate_header(self, request):
        return self.keyword
