from rest_framework import permissions, viewsets

from config.permissions import IsStudent, IsTeacher

from .models import Application, Scholarship, Technology
from .serializers import ApplicationSerializer, ScholarshipSerializer, TechnologySerializer


class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    lookup_field = 'id'

    def get_permissions(self):
        # Apenas professores podem cadastrar, alterar ou deletar tecnologias.
        # Qualquer um (alunos e professores) pode listar.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    lookup_field = 'id'

    def get_permissions(self):
        # Apenas professores gerenciam bolsas. Alunos só podem listar e ver os detalhes.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Associa automaticamente a bolsa ao professor logado que a criou
        serializer.save(orientator_id=self.request.user.id)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'create':
            # Apenas ALUNOS podem se inscrever em bolsas
            return [IsStudent()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Apenas PROFESSORES podem mudar o status da inscrição (ex: Approved, Rejected)
            return [IsTeacher()]

        # Leitura é permitida para os dois (o isolamento é feito no get_queryset)
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Isolamento de dados:
        - Professores veem todas as inscrições.
        - Alunos veem apenas as suas próprias inscrições.
        """
        user = self.request.user
        if getattr(user, 'role', None) == 'TEACHER':
            return Application.objects.all()

        return Application.objects.filter(student_id=user.id)

    def perform_create(self, serializer):
        """
        Como passamos `user_role` e `student_id` para a validação no model,
        nós injetamos isso com segurança diretamente do usuário logado (evitando
        que o aluno forje um payload JSON tentando se passar por outro aluno).
        """
        serializer.save(student_id=self.request.user.id, user_role=getattr(self.request.user, 'role', 'STUDENT'))
