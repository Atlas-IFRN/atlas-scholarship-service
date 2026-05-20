import hashlib
import json

from django.core.cache import cache
from rest_framework.permissions import BasePermission

from apps.scholarship.grpc_client import validate_token


class IsAuthenticatedViaRPC(BasePermission):

    def has_permission(self, request, view):
        token = self._get_token(request)

        if not token:
            return False

        key = "tok:" + hashlib.sha256(token.encode()).hexdigest()
        cached = cache.get(key)
        if cached:
            request.auth_payload = json.loads(cached)
            return True

        payload = validate_token(token)

        if not payload:
            return False

        cache.set(key, json.dumps(payload), timeout=60)
        request.auth_payload = payload
        return True

    def _get_token(self, request):
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth.removeprefix("Bearer ").strip()
        return None


class IsTeacher(BasePermission):
    """
    Bloqueia o acesso se o usuário autenticado não for um Professor.
    """

    def has_permission(self, request, view):
        # Primeiro garante que o IsAuthenticatedViaRPC rodou e injetou o payload
        if hasattr(request, "auth_payload") and request.auth_payload:
            # Altere 'role' para o nome exato da chave que o seu auth-service retorna no gRPC
            return request.auth_payload.get("role") == "TEACHER"
        return False
