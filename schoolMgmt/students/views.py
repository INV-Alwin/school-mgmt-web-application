from rest_framework import viewsets
from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User
from .models import Student
from .serializers import StudentSerializer
from rest_framework import status
from users.permissions import IsAdminOrTeacherReadOnly
from rest_framework.permissions import IsAdminUser
from django.http import HttpResponse
import csv

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrTeacherReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role == 'teacher':
            return Student.objects.filter(assigned_teacher__user=user)
        return Student.objects.none()
    
class StudentMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'student':
            return Response({"detail": "Only students can access this endpoint."}, status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student)
        return Response(serializer.data)

class ExportStudentsCSV(APIView):
    permission_classes = [IsAdmin]  

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'First Name', 'Last Name', 'Email', 'Phone Number',
            'Roll Number', 'Class', 'Date of Birth',
            'Admission Date', 'Status', 'Assigned Teacher'
        ])

        students = Student.objects.select_related('user', 'assigned_teacher').all()
        for student in students:
            writer.writerow([
                student.user.first_name,
                student.user.last_name,
                student.user.email,
                student.user.phone_number,
                student.roll_number,
                student.student_class,
                student.date_of_birth,
                student.admission_date,
                student.status,
                student.assigned_teacher.user.get_full_name() if student.assigned_teacher else "N/A"
            ])

        return response
