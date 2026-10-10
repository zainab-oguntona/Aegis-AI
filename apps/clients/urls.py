from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ClientView(APIView):
    def get(self, request):
        return Response({"client_id": request.user.client_id, "name": request.user.name})


urlpatterns = [
    path("health/", HealthView.as_view()),
    path("client/", ClientView.as_view()),
]
