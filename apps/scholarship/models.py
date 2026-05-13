import uuid

from django.db import models


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

    orientator_id = models.UUIDField(default=uuid.uuid4)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    technologies = models.ManyToManyField(Technology, related_name='scholarships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


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
