import os
import sys

import django

# Força o Python a enxergar a raiz do projeto no Docker
sys.path.insert(0, '/app')

print("o client tá rodando")

# Inicializa o Django (obrigatório para testar o arquivo direto no terminal)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

import grpc
from django.conf import settings

from protos import user_pb2, user_pb2_grpc

# conexão reutilizada (não abre nova a cada request)
_channel = grpc.insecure_channel(settings.AUTH_GRPC_URL)  # "auth-service:50051"
_stub = user_pb2_grpc.AuthServiceStub(_channel)


def validate_token(token: str) -> dict | None:
    try:
        resp = _stub.ValidateToken(
            user_pb2.ValidateTokenRequest(token=token),
            timeout=3,
        )
        if resp.valid:
            return {
                "user_id": resp.user_id,
                "role": resp.role,
                "email": resp.email,
            }
        return None
    except grpc.RpcError as e:
        return None  # auth-service fora, nega acesso
