from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.clients.urls")),
    path("api/v1/", include("apps.risk.urls")),
]
