from django.db import migrations

def delete_students(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    Student.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_alter_student_status'),
    ]

    operations = [
        migrations.RunPython(delete_students),
    ]
