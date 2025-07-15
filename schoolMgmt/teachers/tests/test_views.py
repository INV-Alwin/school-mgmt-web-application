from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from teachers.models import Teacher
import io
from django.core.files.uploadedfile import SimpleUploadedFile
import csv
from datetime import date

class TeacherViewTests(APITestCase):
    def setUp(self):
        # Create admin user and authenticate
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='adminpass', role='admin'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher1@example.com',
            email='teacher1@example.com',
            password='teacherpass',
            role='teacher',
            first_name='John',
            last_name='Doe',
            phone_number='9876543210'
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='TCH001',
            phone='9876543210',
            subject_specialization='Math',
            date_of_joining='2023-01-01',
            status='active'
        )

    def test_list_teachers(self):
        url = reverse('teacher-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_teacher(self):
        url = reverse('teacher-list')
        payload = {
            "user": {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "phone_number": "9998887776"
            },
            "employee_id": "TCH002",
            "phone": "9998887776",
            "subject_specialization": "Physics",
            "date_of_joining": "2024-01-01",
            "status": "active"
        }
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["employee_id"], "TCH002")

    def test_export_teachers_csv(self):
        url = reverse("export-teachers-csv")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode("utf-8")
        self.assertIn("First Name", content)
        self.assertIn("John", content)

    def test_import_teachers_csv(self):
        url = reverse("import-teachers-csv")

        csv_content = """first_name,last_name,email,phone_number,subject_specialization,employee_id,date_of_joining,status
Alice,Wonderland,alice@example.com,9876543211,English,TCH003,2023-06-01,active
Bob,Brown,bob@example.com,9876543212,Chemistry,TCH004,2022-08-15,inactive
"""

        csv_file = SimpleUploadedFile("teachers.csv", csv_content.encode('utf-8'), content_type="text/csv")
        response = self.client.post(url, {'file': csv_file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Successfully imported 2 teachers", response.data["message"])
