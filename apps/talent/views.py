from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.scholarship.models import Application

from .models import InterviewRecord, TalentBankRegistration
from .serializers import InterviewRecordSerializer, TalentBankRegistrationSerializer


@extend_schema(tags=['Banco de talentos'])
class TalentBankRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = TalentBankRegistrationSerializer
    lookup_field = 'id'

    def get_queryset(self):
        if self.action == 'list':
            return TalentBankRegistration.objects.filter(is_actively_looking=True)

        return TalentBankRegistration.objects.all()

    # Endpoint customizado para buscar as inscrições do talento
    # Rota gerada: GET /talents/{id}/applications/
    @action(detail=True, methods=['get'], url_path='applications')
    def get_applications(self, request, id=None):
        # 1. Pega o talento/aluno específico pelo ID da URL
        talent = self.get_object()

        # 2. Busca no app Scholarship as inscrições que pertencem a esse aluno
        applications = Application.objects.filter(student_id=talent.student.id)

        return Response(applications, many=True)


@extend_schema(tags=['Entrevistas'])
class InterviewRecordViewSet(viewsets.ModelViewSet):
    queryset = InterviewRecord.objects.all()
    serializer_class = InterviewRecordSerializer
    lookup_field = 'id'
