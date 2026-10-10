from django.contrib import admin

from .models import APIKey, Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "client_id", "is_active", "created_at")
    search_fields = ("name", "client_id")


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("key_prefix", "client", "is_active", "created_at", "last_used_at")
    readonly_fields = ("key_prefix", "key_hash", "created_at", "last_used_at")
