from django.core.exceptions import ValidationError as DjangoValidationError
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
        fields = ['id', 'title', 'start_date', 'end_date', 'display_order']


# Serializer principal para criação e atualização de bolsas, incluindo os campos relacionados (phases, links, requirements e technologies)
class ScholarshipSerializer(serializers.ModelSerializer):
    phases = ScholarshipPhaseSerializer(many=True)
    links = ScholarshipLinkSerializer(many=True)
    requirements = ScholarshipRequirementSerializer(many=True)
    technologies = TechnologySerializer(many=True, read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            'id',
            'title',
            'description',
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
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'published_by', 'created_at', 'updated_at']

    def validate(self, data):
        if not data.get('links'):
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

    def create(self, validated_data):
        phases_data = validated_data.pop('phases')
        links_data = validated_data.pop('links')
        requirements_data = validated_data.pop('requirements')
        technologies = validated_data.pop('technologies')

        scholarship = Scholarship.objects.create(**validated_data)
        scholarship.technologies.set(technologies)
        self._create_nested(scholarship, phases_data, links_data, requirements_data)

        return scholarship

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
        fields = ['id', 'scholarship', 'student_id', 'student_ira', 'student_period', 'user_role', 'status', 'applied_at']
        read_only_fields = ['id', 'scholarship', 'student_id', 'applied_at']

    def create(self, validated_data):
        validated_data.pop('student_ira', None)
        validated_data.pop('student_period', None)
        validated_data.pop('user_role', None)
        return super().create(validated_data)