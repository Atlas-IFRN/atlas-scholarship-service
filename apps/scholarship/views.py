import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import OuterRef, Prefetch, Subquery
from django.http import Http404
from rest_framework import filters, generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from config.permissions import IsAuthenticatedViaRPC, IsStudent, IsTeacher

from .models import Application, Scholarship, ScholarshipPhase, Technology
from .pagination import Pagination
from .serializers import (
    ApplicationSerializer,
    ScholarshipListSerializer,
    ScholarshipSerializer,
    TechnologySerializer,
)


class ScholarshipQuerysetMixin:
    allowed_status_filters = {'Open', 'Closing', 'Closed'}

    def get_queryset(self):
        payload = self.request.auth_payload
        role = payload.get('role')
        user_id = payload.get('user_id')

        registration_end = ScholarshipPhase.objects.filter(
            scholarship_id=OuterRef('pk'),
            type='Registration',
        ).order_by('display_order', 'end_date').values('end_date')[:1]

        queryset = Scholarship.objects.annotate(
            registration_end=Subquery(registration_end),
        ).prefetch_related('phases', 'links', 'requirements', 'technologies')

        if role == 'STUDENT':
            queryset = queryset.filter(status='Open').prefetch_related(
                Prefetch(
                    'applications',
                    queryset=Application.objects.filter(
                        student_id=user_id,
                        status__in=['Enrolled', 'Approved', 'Rejected'],
                    ).order_by('-updated_at'),
                    to_attr='current_user_applications',
                )
            )

        requested_status = self.request.query_params.get('status')
        if requested_status:
            if requested_status not in self.allowed_status_filters:
                raise ValidationError({
                    'detail': 'Status inválido. Use Open, Closing ou Closed.',
                    'code': 'invalid_status_filter',
                })
            queryset = queryset.filter(status=requested_status)

        technology_id = self.request.query_params.get('technology')
        if technology_id:
            try:
                technology_id = uuid.UUID(technology_id)
            except (TypeError, ValueError, DjangoValidationError):
                raise ValidationError({
                    'detail': 'O filtro technology deve ser um UUID válido.',
                    'code': 'invalid_technology_filter',
                })
            queryset = queryset.filter(technologies__id=technology_id)

        return queryset.order_by('-created_at')

    def get_object(self):
        try:
            return super().get_object()
        except (Http404, NotFound):
            raise NotFound({
                'detail': 'Bolsa não encontrada.',
                'code': 'not_found',
            })


class ScholarshipListCreateView(ScholarshipQuerysetMixin, generics.ListCreateAPIView):
    pagination_class = Pagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['registration_end', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScholarshipSerializer
        return ScholarshipListSerializer

    def perform_create(self, serializer):
        serializer.save(published_by=self.request.auth_payload.get('user_id'))


class ScholarshipDetailView(ScholarshipQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScholarshipSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]


class ApplicationQuerysetMixin:
    def get_queryset(self):
        payload = self.request.auth_payload
        queryset = Application.objects.select_related('scholarship').order_by('-applied_at')

        if payload.get('role') == 'TEACHER':
            return queryset
        return queryset.filter(student_id=payload.get('user_id'))


class ApplicationListView(ApplicationQuerysetMixin, generics.ListAPIView):
    pagination_class = Pagination
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedViaRPC, IsStudent | IsTeacher]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['status', 'applied_at', 'updated_at']
    ordering = ['-applied_at']
    
    
class ApplicationDetailView(ApplicationQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedViaRPC, IsStudent]

    def create(self, request, *args, **kwargs):
        payload = request.auth_payload
        scholarship_id = self.kwargs['scholarship_id']
        student_id = payload.get('user_id')

        try:
            scholarship = Scholarship.objects.get(id=scholarship_id)
        except Scholarship.DoesNotExist:
            raise NotFound({'detail': 'Bolsa não encontrada.', 'code': 'not_found'})

        if scholarship.status != 'Open':
            raise ValidationError({
                'detail': 'O prazo de inscrição para esta bolsa foi encerrado.',
                'code': 'registration_closed',
            })

        student_ira = payload.get('ira')
        student_period = payload.get('period')
        student_role = payload.get('role')

        existing = Application.objects.filter(
            scholarship=scholarship,
            student_id=student_id,
        ).first()

        if existing and existing.status != 'Cancelled':
            raise ValidationError({
                'detail': 'Você já se candidatou para esta bolsa.',
                'code': 'already_applied',
            })

        application = existing or Application(
            scholarship=scholarship,
            student_id=student_id,
        )
        application.status = 'Enrolled'
        application._student_ira = student_ira
        application._student_period = student_period
        application._student_role = student_role

        try:
            application.full_clean()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict)

        application.save()
        serializer = self.get_serializer(application)
        response_status = status.HTTP_200_OK if existing else status.HTTP_201_CREATED
        return Response(serializer.data, status=response_status)


class ApplicationCancelView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedViaRPC, IsStudent]
    http_method_names = ['patch']

    def get_object(self):
        payload = self.request.auth_payload
        try:
            return Application.objects.get(
                scholarship_id=self.kwargs['scholarship_id'],
                student_id=payload.get('user_id'),
                status='Enrolled',
            )
        except Application.DoesNotExist:
            raise NotFound({
                'detail': 'Candidatura não encontrada.',
                'code': 'not_found',
            })

    def perform_update(self, serializer):
        serializer.save(status='Cancelled')


class TechnologyListCreateView(generics.ListCreateAPIView):
    queryset = Technology.objects.all().order_by('name')
    serializer_class = TechnologySerializer
    pagination_class = Pagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name']
    ordering = ['name']
