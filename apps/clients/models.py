import hashlib
import secrets

from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=160)
    client_id = models.CharField(max_length=32, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    enabled_modules = models.JSONField(default=list)
    rate_limit = models.PositiveIntegerField(default=60)
    policy = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = f"cli_{secrets.token_urlsafe(16)}"
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_authenticated(self):
        return self.is_active


class APIKey(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="api_keys")
    key_prefix = models.CharField(max_length=12, editable=False)
    key_hash = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue(cls, client):
        raw_key = f"aegis_{secrets.token_urlsafe(32)}"
        instance = cls.objects.create(client=client, key_prefix=raw_key[:12], key_hash=cls.digest(raw_key))
        return instance, raw_key

    @staticmethod
    def digest(raw_key):
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
