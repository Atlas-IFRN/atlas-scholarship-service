from django.utils import timezone
from rest_framework import filters, generics
from rest_framework.exceptions import NotFound, ValidationError

from config.permissions import IsAuthenticatedViaRPC, IsStudent, IsTeacher

from .models import Note, Talent
from .pagination import Pagination
from .serializers import NoteSerializer, TalentSerializer


class TalentQuerysetMixin:
    allowed_status_filters = {'Active'}

    def get_queryset(self):
        payload = self.request.auth_payload
        role = payload.get('role')
        queryset = Talent.objects.all()

        if role == 'TEACHER':
            queryset = queryset.filter(status='Active')
        else:
            queryset = queryset.filter(student_id=payload.get('user_id'))

        requested_status = self.request.query_params.get('status')
        if requested_status:
            if requested_status not in self.allowed_status_filters:
                raise ValidationError({
                    'detail': 'Status inválido. Use Active.',
                    'code': 'invalid_status_filter',
                })
            queryset = queryset.filter(status=requested_status)

        return queryset.order_by('-joined_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['auth_payload'] = getattr(self.request, 'auth_payload', None) or {}
        return context


class TalentListCreateView(TalentQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = TalentSerializer
    pagination_class = Pagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['joined_at', 'status_changed_at']
    ordering = ['-joined_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticatedViaRPC(), IsStudent()]
        return [IsAuthenticatedViaRPC(), IsTeacher()]

    def perform_create(self, serializer):
        serializer.save(
            student_id=self.request.auth_payload.get('user_id'),
            status_changed_by=self.request.auth_payload.get('user_id'),
            status_changed_at=timezone.now(),
        )


class TalentDeactivateView(TalentQuerysetMixin, generics.UpdateAPIView):
    serializer_class = TalentSerializer
    permission_classes = [IsAuthenticatedViaRPC, IsStudent]
    http_method_names = ['patch']

    def get_object(self):
        try:
            talent = Talent.objects.get(
                student_id=self.request.auth_payload.get('user_id'),
            )
        except Talent.DoesNotExist:
            raise NotFound({
                'detail': 'Registro no banco de talentos não encontrado.',
                'code': 'not_found',
            })

        if talent.status != 'Active':
            raise ValidationError({
                'detail': 'O talento já está inativo.',
                'code': 'talent_already_inactive',
            })
        return talent

    def perform_update(self, serializer):
        serializer.save(
            status='Inactive',
            status_changed_by=self.request.auth_payload.get('user_id'),
            status_changed_at=timezone.now(),
        )


class TalentActivateView(TalentQuerysetMixin, generics.UpdateAPIView):
    serializer_class = TalentSerializer
    permission_classes = [IsAuthenticatedViaRPC, IsStudent]
    http_method_names = ['patch']

    def get_object(self):
        try:
            talent = Talent.objects.get(
                student_id=self.request.auth_payload.get('user_id'),
            )
        except Talent.DoesNotExist:
            raise NotFound({
                'detail': 'Registro no banco de talentos não encontrado.',
                'code': 'not_found',
            })

        if talent.status != 'Inactive':
            raise ValidationError({
                'detail': 'O talento já está ativo.',
                'code': 'talent_already_active',
            })
        return talent

    def perform_update(self, serializer):
        serializer.save(
            status='Active',
            status_changed_by=self.request.auth_payload.get('user_id'),
            status_changed_at=timezone.now(),
        )


class NoteQuerysetMixin:
    def get_queryset(self):
        payload = self.request.auth_payload
        queryset = Note.objects.filter(is_active=True)

        if payload.get('role') != 'TEACHER':
            queryset = queryset.filter(student_id=payload.get('user_id'))

        content = self.request.query_params.get('content')
        if content:
            queryset = queryset.filter(content__icontains=content.strip())

        return queryset.order_by('-created_at')


class NoteListCreateView(NoteQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    pagination_class = Pagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        'student_id',
        'orientador_id',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]

    def perform_create(self, serializer):
        serializer.save(
            orientador_id=self.request.auth_payload.get('user_id'),
        )


class NoteDetailView(NoteQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticatedViaRPC(), IsTeacher()]
        return [IsAuthenticatedViaRPC()]
