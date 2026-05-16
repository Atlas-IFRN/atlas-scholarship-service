import uuid

from django.db import models

from apps.scholarship.models import Application


# BANCO DE TALENTOS
class TalentBankRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.UUIDField(help_text="UUID do aluno registrado no banco de talentos")

    is_actively_looking = models.BooleanField(default=True, verbose_name="Buscando oportunidades?")

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Talento: {self.student.full_name}"


# Entrevistas atreladas ao talento
class InterviewRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Liga a entrevista diretamente ao registro do aluno no Banco de Talentos
    talent_registration = models.ForeignKey(TalentBankRegistration, on_delete=models.CASCADE, related_name='interviews')

    # Se a entrevista foi por causa de uma vaga específica, vincula aqui
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True)

    interviewer_id = models.UUIDField(help_text="UUID do professor")

    description = models.TextField(blank=True, help_text="Notas ou feedback da entrevista")

    interview_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.talent_registration.student.full_name}"
