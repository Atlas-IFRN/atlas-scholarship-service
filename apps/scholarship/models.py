import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Technology(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tecnologia"
        verbose_name_plural = "Tecnologias"

    def __str__(self):
        return self.name


class Scholarship(models.Model):
    STATUS_CHOICES = [('Open', 'Open'), ('Closing', 'Closing'), ('Closed', 'Closed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    value_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_months = models.PositiveIntegerField(default=1, help_text="Duração em meses")
    vacancies = models.PositiveIntegerField(default=1)
    minimum_period = models.PositiveIntegerField(default=1)
    minimum_ira = models.DecimalField(max_digits=4, decimal_places=2)

    registration_start = models.DateTimeField(default=timezone.now)
    registration_end = models.DateTimeField(default=timezone.now)
    orientator_id = models.UUIDField(default=uuid.uuid4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    technologies = models.ManyToManyField(Technology, related_name='scholarships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        # Validação transiente de links passada pelo serializer durante a criação/atualização
        if hasattr(self, '_temporary_links') and not self._temporary_links:
            raise ValidationError({"links": "A bolsa deve possuir pelo menos um link ou edital."})


class ScholarshipLink(models.Model):
    TYPE_CHOICES = [('Edital', 'Edital'), ('Attachment', 'Attachment'), ('Form', 'Form'), ('Other', 'Other')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=255, help_text='Ex: Edital, Anexo I')
    url = models.URLField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Other')
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.label} - {self.scholarship.title}"


class ScholarshipRequirement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='requirements')
    title = models.CharField(max_length=100)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.title} - {self.scholarship.title}"


class ScholarshipPhase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='phases')
    title = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.title} - {self.scholarship.title}"


class Application(models.Model):
    STATUS_CHOICES = [('Enrolled', 'Enrolled'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications')
    student_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Enrolled')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('scholarship', 'student_id')

    def clean(self):
        super().clean()

        user_role = getattr(self, '_student_role', None)
        student_ira = getattr(self, '_student_ira', None)

        if user_role == 'TEACHER':
            raise ValidationError({"user_role": "Professores não podem se inscrever em bolsas."})

        # SE ESTIVER ADICIONANDO (Ou seja, se for uma CRIAÇÃO/POST)
        if self._state.adding:
            now = timezone.now()

            if student_ira is not None and self.scholarship:
                if student_ira < self.scholarship.minimum_ira:
                    raise ValidationError({"student_ira": f"IRA insuficiente. Mínimo: {self.scholarship.minimum_ira}"})

            if self.scholarship:
                if not self.scholarship.registration_start or not self.scholarship.registration_end:
                    raise ValidationError({"scholarship": "Datas de inscrição não definidas para esta bolsa."})

                if not (self.scholarship.registration_start <= now <= self.scholarship.registration_end):
                    raise ValidationError(
                        {
                            "scholarship": f"Inscrições fora do prazo. Aberto de {self.scholarship.registration_start.strftime('%d/%m/%Y')} até {self.scholarship.registration_end.strftime('%d/%m/%Y')}."
                        }
                    )

            if self.student_id and self.scholarship:
                active_apps = Application.objects.filter(student_id=self.student_id, status='Approved')
                for app in active_apps:
                    end_of_scholarship = app.applied_at + timezone.timedelta(
                        days=app.scholarship.duration_in_months * 30
                    )
                    if now < end_of_scholarship:
                        raise ValidationError(
                            {"student_id": f"Você já possui uma bolsa ativa até {end_of_scholarship.date()}."}
                        )
