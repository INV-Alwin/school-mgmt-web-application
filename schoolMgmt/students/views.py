from rest_framework import viewsets
from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsAdminOrTeacher

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role == 'teacher':
            return Student.objects.filter(assigned_teacher__user=user)
        return Student.objects.none()
