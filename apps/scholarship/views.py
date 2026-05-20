from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from config.permissions import IsAuthenticatedViaRPC, IsStudent, IsTeacher

from .models import Application, Scholarship, Technology
from .serializers import ApplicationSerializer, ScholarshipSerializer, TechnologySerializer


def _ensure_scholarship_owner(scholarship: Scholarship, request) -> None:
    """Bloqueia ação se o usuário logado não for o orientador da bolsa."""
    user_id = request.auth_payload.get('id') if getattr(request, 'auth_payload', None) else None
    if str(scholarship.orientator_id) != str(user_id):
        raise PermissionDenied("Apenas o orientador da bolsa pode executar esta ação.")


class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'close']:
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        if self.action == 'me_orienting':
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]

    def perform_create(self, serializer):
        serializer.save(orientator_id=self.request.auth_payload.get('id'))

    @action(detail=True, methods=['post'])
    def close(self, request, id=None):
        """Fecha inscrições manualmente (status -> Closed). Apenas o orientador."""
        scholarship = self.get_object()
        _ensure_scholarship_owner(scholarship, request)

        if scholarship.status == 'Closed':
            raise ValidationError({"status": "Bolsa já está fechada."})

        scholarship.status = 'Closed'
        scholarship.save()
        return Response(ScholarshipSerializer(scholarship).data)

    @action(detail=False, methods=['get'], url_path='me/orienting')
    def me_orienting(self, request):
        """Bolsas do professor atual + contagem de inscritos."""
        user_id = request.auth_payload.get('id')
        scholarships = Scholarship.objects.filter(orientator_id=user_id).order_by('-created_at')

        results = []
        for s in scholarships:
            results.append({
                'id': str(s.id),
                'title': s.title,
                'status': s.status,
                'vacancies': s.vacancies,
                'value_per_month': str(s.value_per_month),
                'applications_count': s.applications.count(),
                'registration_start': s.registration_start,
                'registration_end': s.registration_end,
                'created_at': s.created_at,
            })
        return Response(results)

    @action(detail=True, methods=['get'])
    def applications(self, request, id=None):
        """Lista candidatos da bolsa. Apenas o orientador. Resolução do auth fica a cargo do FE."""
        scholarship = self.get_object()
        _ensure_scholarship_owner(scholarship, request)

        qs = scholarship.applications.all().order_by('-applied_at')
        return Response(ApplicationSerializer(qs, many=True).data)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticatedViaRPC(), IsStudent()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        if self.action in ['approve', 'reject']:
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        if self.action == 'withdraw':
            return [IsAuthenticatedViaRPC(), IsStudent()]
        return [IsAuthenticatedViaRPC()]

    def get_queryset(self):
        payload = self.request.auth_payload
        role = payload.get('role')

        if role == 'TEACHER':
            return Application.objects.all()

        return Application.objects.filter(student_id=payload.get('id'))

    def perform_create(self, serializer):
        payload = self.request.auth_payload
        serializer.save(student_id=payload.get('id'), user_role=payload.get('role', 'STUDENT'))

    @action(detail=True, methods=['post'])
    def withdraw(self, request, id=None):
        """Aluno cancela a própria candidatura."""
        application = self.get_object()
        user_id = request.auth_payload.get('id')
        if str(application.student_id) != str(user_id):
            raise PermissionDenied("Você só pode cancelar a sua própria candidatura.")

        if application.status == 'Approved':
            raise ValidationError({"status": "Candidaturas já aprovadas não podem ser canceladas. Procure o orientador."})
        if application.status == 'Rejected':
            raise ValidationError({"status": "Candidatura já está como Rejected."})

        application.delete()
        return Response({"detail": "Candidatura cancelada."}, status=204)

    @action(detail=True, methods=['post'])
    def approve(self, request, id=None):
        """Professor aprova candidato. Só o orientador da bolsa."""
        application = self.get_object()
        _ensure_scholarship_owner(application.scholarship, request)

        if application.status == 'Approved':
            raise ValidationError({"status": "Candidatura já está aprovada."})

        application.status = 'Approved'
        application.updated_at = timezone.now()
        application.save()
        return Response(ApplicationSerializer(application).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, id=None):
        """Professor rejeita candidato. Só o orientador da bolsa."""
        application = self.get_object()
        _ensure_scholarship_owner(application.scholarship, request)

        if application.status == 'Rejected':
            raise ValidationError({"status": "Candidatura já está rejeitada."})

        application.status = 'Rejected'
        application.updated_at = timezone.now()
        application.save()
        return Response(ApplicationSerializer(application).data)
