from django.test import TestCase
from teachers.serializers import TeacherSerializer
from users.models import User
from teachers.models import Teacher
from datetime import date

class TeacherSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "user": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "1234567890"
            },
            "employee_id": "T999",
            "subject_specialization": "Science",
            "date_of_joining": "2023-01-01",
            "status": "active"
        }

    def test_valid_teacher_serializer(self):
        serializer = TeacherSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_duplicate_employee_id(self):
        user = User.objects.create_user(
            username="john.doe@example.com",
            email="john.doe@example.com",
            password="pass",
            role="teacher"
        )
        Teacher.objects.create(
            user=user,
            employee_id="T999",
            phone="1234567890",
            subject_specialization="Math",
            date_of_joining=date(2022, 1, 1),
            status="active"
        )
        serializer = TeacherSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("employee_id", serializer.errors)

    def test_invalid_phone_number(self):
        data = self.valid_data.copy()
        data["user"]["phone_number"] = "12345"
        serializer = TeacherSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors["user"])
