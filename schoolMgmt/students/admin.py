from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_number', 'grade', 'assigned_teacher', 'status']
    search_fields = ['user__username', 'roll_number']
    list_filter = ['grade', 'status']

