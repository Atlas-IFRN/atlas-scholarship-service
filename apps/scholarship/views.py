from django.utils import timezone
from rest_framework import generics
from config.permissions import IsAuthenticatedViaRPC, IsStudent, IsTeacher

from .models import Application, Scholarship, Technology
from .serializers import ApplicationSerializer, ScholarshipSerializer, ScholarshipListSerializer, TechnologySerializer
from .pagination import Pagination

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404



# ainda temos que testar a criação de bolsas, mas a listagem e detalhes já estão funcionando
# o problema é que não tenho um usuário professor no banco e não consigo testar a criação apenas alterando o registro de usuario no banco
# então vou deixar para testar depois, quando tiver um usuario professor criado
class ScholarshipListCreateView(generics.ListCreateAPIView):
    pagination_class = Pagination
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScholarshipSerializer
        return ScholarshipListSerializer

    def get_queryset(self):
        payload = self.request.auth_payload
        user_role = payload.get('role')
        
        queryset = Scholarship.objects.all()

        if user_role == 'STUDENT':
            # estudantes veem bolsas abertas ou com status === "RegistrationClosed"
            queryset = queryset.filter(status__in=['Open', 'RegistrationClosed'])

        return queryset

    def perform_create(self, serializer):
        payload = self.request.auth_payload
        serializer.save(published_by=payload.get('user_id'))


class ScholarshipDetailView(generics.RetrieveAPIView):
    serializer_class = ScholarshipSerializer

    def get_object(self):
        try:
            return Scholarship.objects.prefetch_related(
                'phases', 'links', 'requirements', 'technologies'
            ).get(id=self.kwargs['pk'])
        except Scholarship.DoesNotExist:
            raise NotFound({
                'detail': 'Bolsa não encontrada.',
                'code': 'not_found',
            })
            

class ApplicationListView(generics.ListAPIView):
    pagination_class = Pagination
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedViaRPC]

    def get_queryset(self):
        payload = self.request.auth_payload

        if payload.get('role') == 'TEACHER':
            # mostrar todas as incrições para professores menos as que tem status "Cancelled"
            return Application.objects.all().exclude(status='Cancelled')

        return Application.objects.filter(student_id=payload.get('user_id'))


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedViaRPC]

    def create(self, request, *args, **kwargs):
        payload = request.auth_payload
        scholarship_id = self.kwargs["scholarship_id"]
        student_id = payload.get("user_id")

        try:
            scholarship = Scholarship.objects.get(id=scholarship_id)
        except Scholarship.DoesNotExist:
            raise NotFound({"detail": "Bolsa não encontrada.", "code": "not_found"})

        if scholarship.status != "Open":
            raise ValidationError({
                "detail": "O prazo de inscrição para esta bolsa foi encerrado.",
                "code": "registration_closed",
            })

        student_ira = payload.get("ira")
        student_period = payload.get("period")
        # por algum motivo o ira e period estão vindo como None, devo analisar isso com Ayrton, mas por enquanto vou deixar assim 
        # para não travar o desenvolvimento, já que o mais importante é o role, que está vindo corretamente
        
        student_role = payload.get("role")
        
        print(f"Student IRA: {student_ira}, Period: {student_period}, Role: {student_role}")

        if student_role != "STUDENT":
            raise ValidationError({
                "detail": "Apenas estudantes podem se inscrever para as bolsas.",
                "code": "teacher_cannot_apply",
            })

        existing = Application.objects.filter(
            scholarship=scholarship,
            student_id=student_id,
        ).first()

        if existing:
            if existing.status == "Enrolled":
                raise ValidationError({
                    "detail": "Você já se candidatou para esta bolsa.",
                    "code": "already_applied",
                })

            if existing.status == "Cancelled":
                existing.status = "Enrolled"
                existing._student_ira = student_ira
                existing._student_period = student_period
                existing._student_role = student_role

                try:
                    existing.full_clean()
                except ValidationError as e:
                    raise ValidationError(e.message_dict)

                existing.save()
                serializer = self.get_serializer(existing)
                return Response(serializer.data, status=status.HTTP_200_OK)

        application = Application(
            scholarship=scholarship,
            student_id=student_id,
        )
        application._student_ira = student_ira
        application._student_period = student_period
        application._student_role = student_role

        try:
            application.full_clean()
        except ValidationError as e:
            raise ValidationError(e.message_dict)

        application.save()
        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationCancelView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedViaRPC, IsStudent]
    http_method_names = ['patch']

    def get_object(self):
        payload = self.request.auth_payload
        
        return get_object_or_404(
            Application,
            scholarship_id=self.kwargs['scholarship_id'],
            student_id=payload.get('user_id'),
            status='Enrolled',
        )

    def perform_update(self, serializer):
        serializer.save(status='Cancelled')


class TechnologyListView(generics.ListAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    