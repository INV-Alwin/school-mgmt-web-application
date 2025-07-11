from django.db import migrations

def delete_teachers(apps, schema_editor):
    Teacher = apps.get_model('teachers', 'Teacher')
    Teacher.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(delete_teachers),
    ]
