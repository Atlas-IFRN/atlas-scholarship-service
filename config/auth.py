# mock_auth.py
from rest_framework.authentication import BaseAuthentication


class RemoteUser:
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = role
        self.is_authenticated = True


class DevMockAuthentication(BaseAuthentication):
    """
    Autenticação temporária para testes locais.
    Lê a Role e o ID diretamente dos Headers da requisição.
    """

    def authenticate(self, request):
        role = request.headers.get('X-Mock-Role', 'TEACHER')
        user_id = request.headers.get('X-Mock-User-ID', '00000000-0000-0000-0000-000000000001')

        user = RemoteUser(user_id=user_id, role=role)
        return (user, None)
