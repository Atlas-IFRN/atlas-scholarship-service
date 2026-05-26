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
    class Meta:
        model = Talent
        fields = '__all__'
        read_only_fields = ['id', 'student_id', 'status_changed_by', 'status_changed_at', 'joined_at']

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

        auth_payload = self.context.get('auth_payload') or {}
        instance._user_role = auth_payload.get('role', 'STUDENT')
        if not self.instance:
            instance.student_id = auth_payload.get('user_id')

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))

        return data
