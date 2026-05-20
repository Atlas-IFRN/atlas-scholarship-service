from rest_framework import viewsets

# Importando apenas a nossa permissão unificada por RPC
from config.permissions import IsAuthenticatedViaRPC

from .models import Application, Scholarship, Technology
from .serializers import ApplicationSerializer, ScholarshipSerializer, TechnologySerializer


class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    lookup_field = 'id'

    def get_permissions(self):
        # Apenas professores gerenciam tecnologias. Qualquer logado pode listar/ver.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticatedViaRPC(allowed_roles=['TEACHER'])]
        return [IsAuthenticatedViaRPC()]


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    lookup_field = 'id'

    def get_permissions(self):
        # Apenas professores gerenciam bolsas. Alunos só listam e veem detalhes.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticatedViaRPC(allowed_roles=['TEACHER'])]
        return [IsAuthenticatedViaRPC()]

    def perform_create(self, serializer):
        # Associa automaticamente a bolsa ao ID do professor vindo do gRPC
        serializer.save(orientator_id=self.request.auth_payload.get('id'))


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'create':
            # Apenas ALUNOS podem se inscrever em bolsas
            return [IsAuthenticatedViaRPC(allowed_roles=['STUDENT'])]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Apenas PROFESSORES podem mudar o status da inscrição (ex: Approved, Rejected)
            return [IsAuthenticatedViaRPC(allowed_roles=['TEACHER'])]

        # Leitura é permitida para os dois (o isolamento é feito no get_queryset)
        return [IsAuthenticatedViaRPC()]

    def get_queryset(self):
        """
        Isolamento de dados:
        - Professores veem todas as inscrições.
        - Alunos veem apenas as suas próprias inscrições.
        """
        payload = self.request.auth_payload
        role = payload.get('role')

        if role == 'TEACHER':
            return Application.objects.all()

        return Application.objects.filter(student_id=payload.get('id'))

    def perform_create(self, serializer):
        """Injeta os dados de segurança do aluno vindos do token validado."""
        payload = self.request.auth_payload
        serializer.save(student_id=payload.get('id'), user_role=payload.get('role', 'STUDENT'))
