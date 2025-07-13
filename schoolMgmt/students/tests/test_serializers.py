from rest_framework.test import APITestCase
from students.serializers import StudentSerializer
from users.models import User
from teachers.models import Teacher
from students.models import Student
from datetime import date

class StudentSerializerTest(APITestCase):

    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='teach',
            email='teach@example.com',
            password='teacher@123',
            role='teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            subject_specialization='Science',
            employee_id='EMP123',
            date_of_joining='2022-01-01',
            status='Active'
        )

    def get_valid_data(self):
        return {
            "user": {
                "first_name": "Alwin",
                "last_name": "Yesudas",
                "email": "alwin@example.com",
                "phone_number": "9876543210"
            },
            "roll_number": "STU123",
            "student_class": "10B",
            "date_of_birth": str(date(2006, 5, 10)),
            "admission_date": str(date(2022, 6, 1)),
            "status": "active",
            "assigned_teacher": self.teacher.id
        }

    def test_valid_student_serializer(self):
        data = self.get_valid_data()
        serializer = StudentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        student = serializer.save()
        self.assertEqual(student.roll_number, data["roll_number"])
        self.assertEqual(student.user.email, data["user"]["email"])

    def test_duplicate_roll_number(self):
        data = self.get_valid_data()
        # First creation
        serializer1 = StudentSerializer(data=data)
        self.assertTrue(serializer1.is_valid(), serializer1.errors)
        serializer1.save()

        # Second creation with same roll_number
        data["user"]["email"] = "different@example.com"
        data["user"]["phone_number"] = "1234567890"
        serializer2 = StudentSerializer(data=data)
        self.assertFalse(serializer2.is_valid())
        self.assertIn("roll_number", serializer2.errors)

    def test_duplicate_email(self):
        User.objects.create_user(
            username='alwin@example.com',
            email='alwin@example.com',
            password='student@123',
            role='student'
        )

        data = self.get_valid_data()
        serializer = StudentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_invalid_phone_number(self):
        data = self.get_valid_data()
        data["user"]["phone_number"] = "1234"  # too short
        serializer = StudentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)
