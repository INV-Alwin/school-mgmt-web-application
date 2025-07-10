from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'subject_specialization', 'status']
    search_fields = ['user__username', 'employee_id', 'subject_specialization']
    list_filter = ['status']
