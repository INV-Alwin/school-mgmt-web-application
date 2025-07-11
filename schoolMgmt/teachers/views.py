from rest_framework import viewsets
from .models import Teacher
from .serializers import TeacherSerializer
from users.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.http import HttpResponse
import csv

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdmin]

class ExportTeachersCSV(APIView):
    permission_classes = [IsAdmin]  

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teachers.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'First Name', 'Last Name', 'Email', 'Phone Number',
            'Subject Specialization', 'Employee ID', 'Date of Joining', 'Status'
        ])

        teachers = Teacher.objects.select_related('user').all()
        for teacher in teachers:
            writer.writerow([
                teacher.user.first_name,
                teacher.user.last_name,
                teacher.user.email,
                teacher.user.phone_number,
                teacher.subject_specialization,
                teacher.employee_id,
                teacher.date_of_joining,
                teacher.status
            ])

        return response
