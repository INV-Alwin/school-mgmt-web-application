from rest_framework import viewsets, status
from .models import Teacher
from users.models import User
from .serializers import TeacherSerializer
from users.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.http import HttpResponse
from rest_framework.response import Response
import csv
import io

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdmin]

class ImportTeachersCSV(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded_file))

        created_count = 0
        for row in reader:
            if User.objects.filter(email=row['email']).exists():
                continue  # Skip if email already exists

            user = User.objects.create_user(
                username=row['email'],
                email=row['email'],
                password='teacher@123',
                role='teacher',
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone_number=row['phone_number']
            )

            Teacher.objects.create(
                user=user,
                subject_specialization=row['subject_specialization'],
                employee_id=row['employee_id'],
                date_of_joining=row['date_of_joining'],
                status=row['status'].lower()
            )
            created_count += 1

        return Response({'message': f'Successfully imported {created_count} teachers'}, status=status.HTTP_201_CREATED)


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
