from django.db import transaction
from rest_framework import serializers

from .models import Application, Scholarship, ScholarshipLink, ScholarshipPhase, ScholarshipRequirement, Technology


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = '__all__'


class ScholarshipLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipLink
        fields = ['id', 'label', 'url', 'display_order']


class ScholarshipRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipRequirement
        fields = ['id', 'title', 'description', 'display_order']


class ScholarshipPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipPhase
        fields = ['id', 'title', 'start_date', 'end_date', 'type', 'display_order']


class TechnologyRelatedField(serializers.PrimaryKeyRelatedField):
    """Accept technology UUIDs while preserving the nested response contract."""

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.get('id')
        return super().to_internal_value(data)

    def to_representation(self, value):
        return TechnologySerializer(value).data


# Serializer principal para criação e atualização de bolsas, incluindo os campos relacionados (phases, links, requirements e technologies)
class ScholarshipSerializer(serializers.ModelSerializer):
    phases = ScholarshipPhaseSerializer(many=True)
    links = ScholarshipLinkSerializer(many=True)
    requirements = ScholarshipRequirementSerializer(many=True)
    technologies = TechnologyRelatedField(queryset=Technology.objects.all(), many=True)
    user_application = serializers.SerializerMethodField()

    class Meta:
        model = Scholarship
        fields = [
            'id',
            'title',
            'description',
            'activity_description',
            'value_per_month',
            'duration_in_months',
            'vacancies',
            'minimum_period',
            'minimum_ira',
            'published_by',
            'status',
            'phases',
            'links',
            'requirements',
            'technologies',
            'user_application',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'published_by', 'created_at', 'updated_at']

    def get_user_application(self, scholarship):
        request = self.context.get('request')
        payload = getattr(request, 'auth_payload', {}) if request else {}

        if payload.get('role') != 'STUDENT':
            return None

        applications = getattr(scholarship, 'current_user_applications', None)
        if applications is None:
            application = scholarship.applications.filter(
                student_id=payload.get('user_id'),
                status__in=['Enrolled', 'Approved', 'Rejected'],
            ).first()
        else:
            application = applications[0] if applications else None

        if application is None:
            return {
                'applied': False,
                'application_id': None,
                'status': None,
            }

        return {
            'applied': True,
            'application_id': str(application.id),
            'status': application.status,
        }

    def validate(self, data):
        links = data.get('links')
        if (self.instance is None and not links) or ('links' in data and not links):
            raise serializers.ValidationError(
                {"links": "A bolsa deve possuir pelo menos um link para redirecionar os alunos ao edital."}
            )
        return data

    def _create_nested(self, scholarship, phases, links, requirements):
        ScholarshipPhase.objects.bulk_create(
            [ScholarshipPhase(scholarship=scholarship, **p) for p in phases]
        )
        ScholarshipLink.objects.bulk_create(
            [ScholarshipLink(scholarship=scholarship, **l) for l in links]
        )
        ScholarshipRequirement.objects.bulk_create(
            [ScholarshipRequirement(scholarship=scholarship, **r) for r in requirements]
        )

    @transaction.atomic
    def create(self, validated_data):
        phases_data = validated_data.pop('phases')
        links_data = validated_data.pop('links')
        requirements_data = validated_data.pop('requirements')
        technologies = validated_data.pop('technologies')

        scholarship = Scholarship.objects.create(**validated_data)
        scholarship.technologies.set(technologies)
        self._create_nested(scholarship, phases_data, links_data, requirements_data)

        return scholarship

    @transaction.atomic
    def update(self, instance, validated_data):
        phases_data = validated_data.pop('phases', None)
        links_data = validated_data.pop('links', None)
        requirements_data = validated_data.pop('requirements', None)
        technologies_data = validated_data.pop('technologies', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if technologies_data is not None:
            instance.technologies.set(technologies_data)

        if phases_data is not None:
            instance.phases.all().delete()
            ScholarshipPhase.objects.bulk_create(
                [ScholarshipPhase(scholarship=instance, **p) for p in phases_data]
            )

        if links_data is not None:
            instance.links.all().delete()
            ScholarshipLink.objects.bulk_create(
                [ScholarshipLink(scholarship=instance, **l) for l in links_data]
            )

        if requirements_data is not None:
            instance.requirements.all().delete()
            ScholarshipRequirement.objects.bulk_create(
                [ScholarshipRequirement(scholarship=instance, **r) for r in requirements_data]
            )

        return instance


# Serializer para a listagem de bolsas, com menos detalhes (sem os campos relacionados, servirá para os cards de listagem)
class ScholarshipListSerializer(ScholarshipSerializer):
    class Meta(ScholarshipSerializer.Meta):
        fields = [
            f for f in ScholarshipSerializer.Meta.fields
            if f not in ('phases', 'links', 'requirements')
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    student_ira = serializers.DecimalField(max_digits=4, decimal_places=2, write_only=True, required=False)
    student_period = serializers.IntegerField(write_only=True, required=False)
    user_role = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Application
        # nós adicionamos os campos STUDENT_IRA, STUDENT_PERIOD e USER_ROLE para validação, mas eles não são persistidos no model
        fields = [
            'id',
            'scholarship',
            'student_id',
            'student_ira',
            'student_period',
            'user_role',
            'status',
            'applied_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'scholarship', 'student_id', 'applied_at', 'updated_at']

    def create(self, validated_data):
        validated_data.pop('student_ira', None)
        validated_data.pop('student_period', None)
        validated_data.pop('user_role', None)
        return super().create(validated_data)
