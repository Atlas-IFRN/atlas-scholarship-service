from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets

from config.permissions import IsStudent, IsTeacher

from .models import Note, Talent
from .serializers import NoteSerializer, TalentSerializer


@extend_schema(tags=['Banco de talentos'])
class TalentViewSet(viewsets.ModelViewSet):
    serializer_class = TalentSerializer
    lookup_field = 'id'

    def get_permissions(self):
        """Permissões divididas entre alunos (criam) e professores (listam/removem)."""
        if self.action == 'create':
            return [IsStudent()]
        elif self.action in ['list', 'destroy']:
            return [IsTeacher()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Isola os dados do talento ou mostra aos professores a lista dos ativos."""
        user = self.request.user
        role = getattr(user, 'role', None)

        if role == 'TEACHER':
            if self.action == 'list':
                return Talent.objects.filter(status='Active')
            return Talent.objects.all()

        return Talent.objects.filter(student_id=user.id)

    def perform_create(self, serializer):
        """Garante que o aluno inscreva a si mesmo."""
        serializer.save(student_id=self.request.user.id)

    def perform_update(self, serializer):
        """Injeta apenas o ID de quem fez a mudança para fins de auditoria."""
        serializer.save(status_changed_by=self.request.user.id)


@extend_schema(tags=['Notas de entrevistas'])
class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    lookup_field = 'id'

    def get_permissions(self):
        """Notas são criadas e editadas apenas por professores."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Aluno só lê as próprias notas, professor lê todas."""
        user = self.request.user
        if getattr(user, 'role', None) == 'TEACHER':
            return Note.objects.all()
        return Note.objects.filter(student_id=user.id)

    def perform_create(self, serializer):
        """Associa a nota ao professor criador automaticamente."""
        serializer.save(orientador_id=self.request.user.id)
