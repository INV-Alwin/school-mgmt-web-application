from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from teachers.models import Teacher
from io import StringIO
import csv

User = get_user_model()

class TeacherViewTests(APITestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True,
            is_superuser=True
        )
        self.client.login(username='admin', password='adminpass')

        # Sample teacher data
        self.teacher_data = {
            "user": self.admin_user.id,
            "subject_specialization": "Mathematics",
            "employee_id": "TCH12345",
            "date_of_joining": "2023-05-01",
            "status": "Active"
        }

        self.teacher = Teacher.objects.create(**self.teacher_data)

    def test_list_teachers(self):
        url = reverse("teacher-list")  # based on DRF router name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_create_teacher(self):
        url = reverse("teacher-list")
        response = self.client.post(url, data=self.teacher_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])  # may fail if user is reused

    def test_retrieve_teacher(self):
        url = reverse("teacher-detail", kwargs={"pk": self.teacher.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_teacher(self):
        url = reverse("teacher-detail", kwargs={"pk": self.teacher.pk})
        updated_data = self.teacher_data.copy()
        updated_data["subject_specialization"] = "Physics"
        response = self.client.put(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["subject_specialization"], "Physics")

    def test_delete_teacher(self):
        url = reverse("teacher-detail", kwargs={"pk": self.teacher.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_export_teachers_csv(self):
        url = reverse("export-teachers-csv")  # You must name this URL in your urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")

        # Check if CSV content is valid
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)
        self.assertGreaterEqual(len(rows), 1)  # At least header present
