from django.test import TestCase
from users.models import User
from teachers.models import Teacher
from datetime import date

class TeacherModelTest(TestCase):
    def test_create_teacher(self):
        user = User.objects.create_user(
            username="teacher1",
            email="teacher1@example.com",
            password="pass123",
            first_name="Teacher",
            last_name="One",
            role="teacher"
        )
        teacher = Teacher.objects.create(
            user=user,
            employee_id="T101",
            phone="1234567890",
            subject_specialization="Math",
            date_of_joining=date(2020, 5, 1),
            status="active"
        )

        self.assertEqual(str(teacher), "Teacher One (T101)")
        self.assertEqual(teacher.subject_specialization, "Math")
