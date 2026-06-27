import hashlib
import json

from django.core.cache import cache
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission

from apps.scholarship.grpc_client import validate_token


class IsAuthenticatedViaRPC(BasePermission):

    def has_permission(self, request, view):
        token = self._get_token(request)

        if not token:
            raise NotAuthenticated("Token de autenticação não fornecido.")

        key = "tok:" + hashlib.sha256(token.encode()).hexdigest()
        cached = cache.get(key)
        if cached:
            request.auth_payload = json.loads(cached)
            return True

        payload = validate_token(token)

        if not payload:
            raise NotAuthenticated("Token inválido ou expirado.")

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
        payload = getattr(request, "auth_payload", None)
        if not payload:
            raise NotAuthenticated("Token de autenticação não fornecido.")
        if payload.get("role") != "TEACHER":
            raise PermissionDenied("Apenas usuários com perfil de professor podem acessar este recurso.")
        return True


class IsStudent(BasePermission):
    """
    Bloqueia o acesso se o usuário autenticado não for um Aluno.
    """

    def has_permission(self, request, view):
        payload = getattr(request, "auth_payload", None)
        if not payload:
            raise NotAuthenticated("Token de autenticação não fornecido.")
        if payload.get("role") != "STUDENT":
            raise PermissionDenied("Apenas usuários com perfil de aluno podem acessar este recurso.")
        return True
