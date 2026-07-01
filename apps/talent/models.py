import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.UUIDField(help_text="UUID do aluno registrado no banco de talentos")
    orientador_id = models.UUIDField(help_text="UUID do professor orientador")
    content = models.TextField(blank=True, help_text="Notas ou feedback do orientador")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Nota para Aluno {self.student_id} por Orientador {self.orientador_id}"

    def clean(self):
        super().clean()
        if self.student_id == self.orientador_id:
            raise ValidationError("Um professor não pode criar notas para si mesmo.")


class Talent(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.UUIDField(unique=True, help_text="UUID do aluno registrado no banco de talentos")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    status_changed_by = models.UUIDField(help_text="UUID do usuário que alterou", null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Talento: {self.student_id}"
