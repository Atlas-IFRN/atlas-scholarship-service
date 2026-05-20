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
        fields = ['id', 'label', 'url', 'type', 'display_order']


class ScholarshipRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipRequirement
        fields = ['id', 'title', 'description', 'display_order']


class ScholarshipPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipPhase
        fields = ['id', 'title', 'start_date', 'end_date', 'display_order']


class ScholarshipSerializer(serializers.ModelSerializer):
    phases = ScholarshipPhaseSerializer(many=True)
    links = ScholarshipLinkSerializer(many=True)
    requirements = ScholarshipRequirementSerializer(many=True)
    technologies = serializers.PrimaryKeyRelatedField(queryset=Technology.objects.all(), many=True)

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
            'orientator_id',
            'registration_start',
            'registration_end',
            'status',
            'phases',
            'links',
            'requirements',
            'technologies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        # Cria uma instância temporária do model na memória para rodar a validação limpa
        instance = Scholarship(
            **{k: v for k, v in data.items() if k not in ['phases', 'links', 'requirements', 'technologies']}
        )

        # Injeta a lista de links para validação de negócio no model
        instance._temporary_links = data.get('links', [])

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return data

    def create(self, validated_data):
        phases_data = validated_data.pop('phases')
        links_data = validated_data.pop('links')
        reqs_data = validated_data.pop('requirements')
        technologies = validated_data.pop('technologies')

        scholarship = Scholarship.objects.create(**validated_data)

        for phase in phases_data:
            ScholarshipPhase.objects.create(scholarship=scholarship, **phase)
        for link in links_data:
            ScholarshipLink.objects.create(scholarship=scholarship, **link)
        for req in reqs_data:
            ScholarshipRequirement.objects.create(scholarship=scholarship, **req)

        scholarship.technologies.set(technologies)
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
            for phase in phases_data:
                ScholarshipPhase.objects.create(scholarship=instance, **phase)

        if links_data is not None:
            instance.links.all().delete()
            for link in links_data:
                ScholarshipLink.objects.create(scholarship=instance, **link)

        if requirements_data is not None:
            instance.requirements.all().delete()
            for req in requirements_data:
                ScholarshipRequirement.objects.create(scholarship=instance, **req)

        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    student_ira = serializers.DecimalField(max_digits=4, decimal_places=2, write_only=True)
    user_role = serializers.CharField(write_only=True)

    class Meta:
        model = Application
        fields = ['id', 'scholarship', 'student_id', 'student_ira', 'user_role', 'status', 'applied_at']
        read_only_fields = ['id', 'applied_at']

    def validate(self, data):
        if self.instance:
            instance = self.instance
            for attr, value in data.items():
                setattr(instance, attr, value)
        else:
            instance = Application(scholarship=data.get('scholarship'), student_id=data.get('student_id'))

        # Injeta as variáveis transientes necessárias para as regras de negócio no Model
        instance._student_ira = data.get('student_ira')
        instance._student_role = data.get('user_role')

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return data

    def create(self, validated_data):
        validated_data.pop('student_ira', None)
        validated_data.pop('user_role', None)
        return super().create(validated_data)
