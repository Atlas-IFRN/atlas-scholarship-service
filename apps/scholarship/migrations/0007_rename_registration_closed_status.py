from django.db import migrations, models


def rename_registration_closed(apps, schema_editor):
    Scholarship = apps.get_model('scholarship', 'Scholarship')
    Scholarship.objects.filter(status='RegistrationClosed').update(status='Closing')


def restore_registration_closed(apps, schema_editor):
    Scholarship = apps.get_model('scholarship', 'Scholarship')
    Scholarship.objects.filter(status='Closing').update(status='RegistrationClosed')


class Migration(migrations.Migration):
    dependencies = [
        ('scholarship', '0006_alter_application_status'),
    ]

    operations = [
        migrations.RunPython(rename_registration_closed, restore_registration_closed),
        migrations.AlterField(
            model_name='scholarship',
            name='status',
            field=models.CharField(
                choices=[
                    ('Draft', 'Draft'),
                    ('Open', 'Open'),
                    ('Closing', 'Closing'),
                    ('Closed', 'Closed'),
                ],
                default='Open',
                max_length=20,
            ),
        ),
    ]
