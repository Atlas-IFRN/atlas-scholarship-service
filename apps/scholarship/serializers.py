from django.utils import timezone
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
            'status',
            'phases',
            'links',
            'requirements',
            'technologies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_links(self, value):
        if not value:
            raise serializers.ValidationError("A bolsa deve possuir pelo menos um link ou edital.")
        return value

    def create(self, validated_data):
        phases_data = validated_data.pop('phases')
        links_data = validated_data.pop('links')
        reqs_data = validated_data.pop('requirements')
        technologies = validated_data.pop('technologies')

        scholarship = Scholarship.objects.create(**validated_data)

        # Criação dos itens relacionados
        for phase in phases_data:
            ScholarshipPhase.objects.create(scholarship=scholarship, **phase)
        for link in links_data:
            ScholarshipLink.objects.create(scholarship=scholarship, **link)
        for req in reqs_data:
            ScholarshipRequirement.objects.create(scholarship=scholarship, **req)

        scholarship.technologies.set(technologies)
        return scholarship


class ApplicationSerializer(serializers.ModelSerializer):
    student_ira = serializers.DecimalField(max_digits=4, decimal_places=2, write_only=True)
    user_role = serializers.CharField(write_only=True)  # Recebido do Gateway/Auth

    class Meta:
        model = Application
        fields = ['id', 'scholarship', 'student_id', 'student_ira', 'user_role', 'status', 'applied_at']
        read_only_fields = ['id', 'status', 'applied_at']

    def validate(self, data):
        # 1. Professores não podem se inscrever
        if data.get('user_role') == 'PROFESSOR':
            raise serializers.ValidationError("Professores não podem se inscrever em bolsas.")

        scholarship = data['scholarship']
        student_id = data['student_id']
        student_ira = data['student_ira']
        now = timezone.now()

        # 2. IRA Mínimo
        if student_ira < scholarship.minimum_ira:
            raise serializers.ValidationError(f"IRA insuficiente. Mínimo: {scholarship.minimum_ira}")

        # 3. Prazo de Inscrição
        phase = scholarship.phases.filter(title__icontains="Inscrição").first()
        if not phase or not (phase.start_date <= now <= phase.end_date):
            raise serializers.ValidationError("Inscrições fora do prazo ou fase não definida.")

        # 4. Apenas uma bolsa ativa (Lógica de duração)
        active_apps = Application.objects.filter(student_id=student_id, status='Aprovado')
        for app in active_apps:
            # Cálculo: Data de aprovação + meses de duração
            end_of_scholarship = app.applied_at + timezone.timedelta(days=app.scholarship.duration_in_months * 30)
            if now < end_of_scholarship:
                raise serializers.ValidationError(f"Você já possui uma bolsa ativa até {end_of_scholarship.date()}.")

        return data
