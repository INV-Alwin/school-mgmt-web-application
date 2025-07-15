from django.db import models
from users.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    subject_specialization = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')])

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
