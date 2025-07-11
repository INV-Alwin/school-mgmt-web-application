from django.test import RequestFactory, TestCase
from users.models import User
from users.permissions import IsAdmin, IsAdminOrTeacherReadOnly
from rest_framework.views import APIView

class DummyView(APIView):
    permission_classes = []

class PermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin',
            role='admin'
        )

        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacherpass',
            role='teacher'
        )

        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass',
            role='student'
        )

    def test_is_admin_permission(self):
        request = self.factory.get('/')
        request.user = self.admin_user

        permission = IsAdmin()
        self.assertTrue(permission.has_permission(request, DummyView()))

        request.user = self.teacher_user
        self.assertFalse(permission.has_permission(request, DummyView()))

    def test_is_admin_or_teacher_read_only_permission(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        permission = IsAdminOrTeacherReadOnly()
        self.assertTrue(permission.has_permission(request, DummyView()))

        
        request.user = self.teacher_user
        self.assertTrue(permission.has_permission(request, DummyView()))

        
        request = self.factory.post('/')
        request.user = self.teacher_user
        self.assertFalse(permission.has_permission(request, DummyView()))

        
        request = self.factory.get('/')
        request.user = self.student_user
        self.assertFalse(permission.has_permission(request, DummyView()))
