from rest_framework import serializers

from .models import InterviewRecord, TalentBankRegistration


class TalentBankRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentBankRegistration
        fields = '__all__'


class InterviewRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewRecord
        fields = '__all__'
