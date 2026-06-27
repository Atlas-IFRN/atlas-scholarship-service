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

    def clean(self):
        super().clean()
        # Validação simples de coerência
        if self.student_id == self.orientador_id:
            raise ValidationError("Um professor não pode criar notas para si mesmo.")


class Talent(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Fulfilled', 'Fulfilled'), ('Inactive', 'Inactive')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Adicionado unique=True para garantir 1 perfil por aluno
    student_id = models.UUIDField(unique=True, help_text="UUID do aluno registrado no banco de talentos")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    status_changed_by = models.UUIDField(help_text="UUID do usuário que alterou", null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        user_role = getattr(self, '_user_role', None)

        # Só valida regras de transição se for uma atualização (registro já existente)
        if not self._state.adding:
            old_instance = Talent.objects.get(pk=self.pk)

            # Se houve mudança de status
            if old_instance.status != self.status:

                if user_role == 'STUDENT':
                    # O Aluno pode transitar livremente ENTRE 'Active' e 'Inactive'
                    status_permitidos_aluno = {'Active', 'Inactive'}

                    if old_instance.status not in status_permitidos_aluno or self.status not in status_permitidos_aluno:
                        raise ValidationError(
                            {"status": "Alunos só podem alternar o status entre 'Active' e 'Inactive'."}
                        )

                elif user_role == 'TEACHER':
                    # O Professor pode transitar livremente ENTRE 'Active' e 'Fulfilled'
                    status_permitidos_professor = {'Active', 'Fulfilled'}

                    if (
                        old_instance.status not in status_permitidos_professor
                        or self.status not in status_permitidos_professor
                    ):
                        raise ValidationError(
                            {"status": "Professores só podem alternar o status entre 'Active' e 'Fulfilled'."}
                        )

    def __str__(self):
        return f"Talento: {self.student_id}"
