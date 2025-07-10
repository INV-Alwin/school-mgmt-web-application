from rest_framework import viewsets
from .models import Teacher
from .serializers import TeacherSerializer
from users.permissions import IsAdmin

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdmin]
