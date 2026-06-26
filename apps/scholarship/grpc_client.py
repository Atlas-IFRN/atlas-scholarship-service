import os
import sys

import django

sys.path.insert(0, '/app')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

import grpc
from django.conf import settings

from proto import user_pb2, user_pb2_grpc


def _normalize_grpc_url(grpc_url: str) -> str:
    if grpc_url.startswith("0.0.0.0"):
        _, _, port = grpc_url.rpartition(":")
        return f"host.docker.internal:{port or '50051'}"
    return grpc_url


_GRPC_URL = _normalize_grpc_url(getattr(settings, 'AUTH_GRPC_URL', 'auth-service:50051'))
_channel = grpc.insecure_channel(_GRPC_URL)
_auth_stub = user_pb2_grpc.AuthServiceStub(_channel)
_user_stub = user_pb2_grpc.UserServiceStub(_channel)


def validate_token(token: str) -> dict | None:
    try:
        response = _auth_stub.ValidateToken(
            user_pb2.ValidateTokenRequest(token=token),
            timeout=3,
        )
        if response.valid:
            return {
                "user_id": response.user_id,
                "role": response.role,
                "email": response.email,
            }
        return None
    except grpc.RpcError as exc:
        raise RuntimeError(f"Falha ao validar token no auth gRPC ({_GRPC_URL}): {exc.details()}") from exc


def get_user_profile(user_id: str) -> dict | None:
    try:
        response = _user_stub.GetUserProfile(
            user_pb2.UserRequest(matricula=user_id),
            timeout=3,
        )
        if response.id:
            return {
                "id": response.id,
                "matricula": response.matricula,
                "first_name": response.first_name,
                "full_name": response.full_name,
                "email": response.email,
                "role": response.role,
                "ira": float(response.ira) if response.ira is not None else None,
                "period": response.period,
                "about_me": response.about_me,
                "linkedin": response.linkedin,
                "github": response.github,
                "curriculo_lattes": response.curriculo_lattes,
                "course_name": response.course_name,
                "institution_name": response.institution_name,
            }
        return None
    except grpc.RpcError:
        return None
