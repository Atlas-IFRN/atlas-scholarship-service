from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .models import Note, Talent


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

    def validate(self, data):
        # Cria instância temporária e roda o clean do model
        instance = Note(**data)
        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))
        return data


class TalentSerializer(serializers.ModelSerializer):
    # Pode apagar aquela linha: user_role = serializers.CharField(...)

    class Meta:
        model = Talent
        fields = '__all__'
        read_only_fields = ['id', 'status_changed_by', 'status_changed_at', 'joined_at']

    def validate(self, data):
        if self.instance:
            instance = self.instance
            new_status = data.get('status', instance.status)
            if instance.status != new_status:
                data['status_changed_at'] = timezone.now()

            for attr, value in data.items():
                setattr(instance, attr, value)
        else:
            instance = Talent(**data)

        # MÁGICA AQUI: Pegamos o usuário logado direto do contexto da requisição
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Injeta no model a role real de quem fez a requisição
            instance._user_role = getattr(request.user, 'role', 'STUDENT')

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))

        return data
