from django.test import TestCase
from users.models import User

class UserModelTest(TestCase):

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            role=User.Role.ADMIN
        )
        self.assertEqual(user.role, 'admin')
        self.assertEqual(str(user), "adminuser (admin)")

    def test_create_teacher_user(self):
        user = User.objects.create_user(
            username='teacheruser',
            email='teacher@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )
        self.assertEqual(user.role, 'teacher')
        self.assertEqual(str(user), "teacheruser (teacher)")

    def test_create_student_user(self):
        user = User.objects.create_user(
            username='studentuser',
            email='student@example.com',
            password='studentpass123',
            role=User.Role.STUDENT
        )
        self.assertEqual(user.role, 'student')
        self.assertEqual(str(user), "studentuser (student)")
