from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import Application, Scholarship, Technology
from .serializers import ApplicationSerializer, ScholarshipSerializer, TechnologySerializer


# --- SCHOLARSHIP VIEWSET ---
@extend_schema_view(
    list=extend_schema(
        summary="Listar todas as bolsas",
        description="Retorna uma lista de bolsas cadastradas.",
        tags=["Bolsas"],
        responses={200: ScholarshipSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Buscar detalhes de uma bolsa",
        tags=["Bolsas"],
        responses={200: ScholarshipSerializer, 404: OpenApiResponse(description="Bolsa não encontrada.")},
    ),
    create=extend_schema(
        summary="Criar uma nova bolsa",
        description="Cria uma bolsa com suas fases, links e requisitos aninhados.",
        tags=["Bolsas"],
        examples=[
            OpenApiExample(
                'Exemplo Completo de Criação',
                value={
                    "title": "Bolsa de Extensão - IA",
                    "description": "Desenvolvimento de modelos de NLP.",
                    "value_per_month": "800.00",
                    "duration_in_months": 12,
                    "vacancies": 3,
                    "minimum_period": 2,
                    "minimum_ira": "7.50",
                    "orientator_id": "550e8400-e29b-41d4-a716-446655440000",
                    "technologies": ["UUID-TECNOLOGIA-1"],
                    "phases": [
                        {
                            "title": "Inscrições",
                            "start_date": "2026-06-01T00:00:00Z",
                            "end_date": "2026-06-15T23:59:59Z",
                            "display_order": 1,
                        }
                    ],
                    "links": [{"label": "Edital", "url": "https://link.com", "type": "EDITAL", "display_order": 1}],
                    "requirements": [{"title": "Python", "description": "Ter cursado lógica", "display_order": 1}],
                },
                request_only=True,
            )
        ],
        responses={
            201: ScholarshipSerializer,
            400: OpenApiResponse(
                description="Erro de Validação (Bad Request). O payload não atendeu às regras de negócio."
            ),
        },
    ),
    update=extend_schema(summary="Atualizar uma bolsa inteira", tags=["Bolsas"]),
    partial_update=extend_schema(summary="Atualizar parte de uma bolsa", tags=["Bolsas"]),
    destroy=extend_schema(
        summary="Deletar uma bolsa",
        tags=["Bolsas"],
        responses={
            204: OpenApiResponse(description="Deletado com sucesso (No Content)."),
            404: OpenApiResponse(description="Bolsa não encontrada."),
        },
    ),
)
class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    lookup_field = 'id'


# --- APPLICATION VIEWSET ---
@extend_schema_view(
    list=extend_schema(summary="Listar inscrições", tags=["Inscrições"]),
    retrieve=extend_schema(summary="Detalhes da inscrição", tags=["Inscrições"]),
    create=extend_schema(
        summary="Realizar inscrição em uma bolsa",
        tags=["Inscrições"],
        examples=[
            OpenApiExample(
                'Payload de Inscrição',
                value={
                    "scholarship": "UUID-DA-BOLSA",
                    "student_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                    "student_ira": "9.20",
                    "user_role": "ALUNO",
                },
                request_only=True,
            )
        ],
        responses={
            201: ApplicationSerializer,
            400: OpenApiResponse(description="Erro de Validação. Ex: O aluno não é ALUNO ou o IRA é insuficiente."),
        },
    ),
    update=extend_schema(summary="Atualizar inscrição", tags=["Inscrições"]),
    partial_update=extend_schema(summary="Atualizar status da inscrição", tags=["Inscrições"]),
    destroy=extend_schema(summary="Cancelar inscrição", tags=["Inscrições"]),
)
class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = 'id'


# --- TECHNOLOGY VIEWSET ---
@extend_schema_view(
    list=extend_schema(summary="Listar tecnologias", tags=["Tecnologias"]),
    retrieve=extend_schema(summary="Detalhes da tecnologia", tags=["Tecnologias"]),
    create=extend_schema(
        summary="Cadastrar nova tecnologia",
        tags=["Tecnologias"],
        examples=[
            OpenApiExample(
                'Payload de Tecnologia',
                value={"name": "Django"},
                request_only=True,
            )
        ],
        responses={
            201: TechnologySerializer,
            400: OpenApiResponse(description="Erro de validação. Ex: Já existe uma tecnologia com este nome."),
        },
    ),
    update=extend_schema(summary="Atualizar tecnologia", tags=["Tecnologias"]),
    partial_update=extend_schema(summary="Atualizar tecnologia parcialmente", tags=["Tecnologias"]),
    destroy=extend_schema(summary="Deletar tecnologia", tags=["Tecnologias"]),
)
class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    lookup_field = 'id'
