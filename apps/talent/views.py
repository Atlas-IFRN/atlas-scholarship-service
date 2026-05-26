from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from config.permissions import IsAuthenticatedViaRPC, IsTeacher

from .models import Note, Talent
from .serializers import NoteSerializer, TalentSerializer


@extend_schema(tags=['Banco de talentos'])
class TalentViewSet(viewsets.ModelViewSet):
    serializer_class = TalentSerializer
    lookup_field = 'id'

    def get_permissions(self):
        """Permissões divididas usando a nova estrutura baseada em roles do gRPC."""
        if self.action == 'create':
            return [IsAuthenticatedViaRPC()]
        elif self.action in ['list', 'destroy']:
            return [IsAuthenticatedViaRPC(), IsTeacher()]

        # 'retrieve', 'update', 'partial_update' aceitam qualquer um logado,
        # pois o get_queryset se encarrega de isolar o registro do aluno correto.
        return [IsAuthenticatedViaRPC()]

    def get_queryset(self):
        """Isola os dados do talento ou mostra aos professores a lista dos ativos."""
        payload = self.request.auth_payload
        role = payload.get('role')

        if role == 'TEACHER':
            if self.action == 'list':
                return Talent.objects.filter(status='Active')
            return Talent.objects.all()

        return Talent.objects.filter(student_id=payload.get('user_id'))

    def perform_create(self, serializer):
        serializer.save(student_id=self.request.auth_payload.get('user_id'))

    def perform_update(self, serializer):
        """Injeta apenas o ID de quem fez a mudança para fins de auditoria."""
        serializer.save(status_changed_by=self.request.auth_payload.get('user_id'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['auth_payload'] = getattr(self.request, 'auth_payload', None) or {}
        return context


@extend_schema(tags=['Notas de entrevistas'])
class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    lookup_field = 'id'

    def get_permissions(self):
        # Apenas professores podem criar, editar ou deletar notas
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticatedViaRPC(), IsTeacher()]

        return [IsAuthenticatedViaRPC()]

    def get_queryset(self):
        """Aluno só lê as próprias notas, professor lê todas."""
        payload = self.request.auth_payload
        role = payload.get('role')

        if role == 'TEACHER':
            return Note.objects.all()
        return Note.objects.filter(student_id=payload.get('user_id'))

    def perform_create(self, serializer):
        """Associa a nota ao professor criador automaticamente via ID do gRPC."""
        serializer.save(orientador_id=self.request.auth_payload.get('user_id'))
