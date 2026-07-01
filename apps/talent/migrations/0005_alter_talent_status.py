from django.db import migrations, models


def replace_fulfilled_with_inactive(apps, schema_editor):
    Talent = apps.get_model('talent', 'Talent')
    Talent.objects.filter(status='Fulfilled').update(status='Inactive')


class Migration(migrations.Migration):

    dependencies = [
        ('talent', '0004_alter_talent_status_changed_by_and_more'),
    ]

    operations = [
        migrations.RunPython(
            replace_fulfilled_with_inactive,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='talent',
            name='status',
            field=models.CharField(
                choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
                default='Active',
                max_length=20,
            ),
        ),
    ]
