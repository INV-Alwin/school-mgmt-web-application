import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import csv
import io

from students.models import Student
from students.serializers import StudentSerializer
from teachers.models import Teacher
from users.models import User


class StudentModelTest(TestCase):
    """Test cases for Student model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='John',
            last_name='Doe',
            phone_number='1234567890'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            role='teacher',
            first_name='Jane',
            last_name='Smith',
            phone_number='0987654321'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            subject='Mathematics',
            qualification='M.Sc',
            experience_years=5
        )
    
    def test_student_creation(self):
        """Test student model creation"""
        student = Student.objects.create(
            user=self.user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active',
            assigned_teacher=self.teacher
        )
        
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.roll_number, 'STU001')
        self.assertEqual(student.student_class, '10A')
        self.assertEqual(student.status, 'active')
        self.assertEqual(student.assigned_teacher, self.teacher)
    
    def test_student_str_method(self):
        """Test student string representation"""
        student = Student.objects.create(
            user=self.user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active'
        )
        
        expected_str = f"{self.user.get_full_name()} (STU001)"
        self.assertEqual(str(student), expected_str)
    
    def test_roll_number_uniqueness(self):
        """Test roll number uniqueness constraint"""
        Student.objects.create(
            user=self.user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active'
        )
        
        # Create another user for second student
        user2 = User.objects.create_user(
            username='student2@test.com',
            email='student2@test.com',
            password='testpass123',
            role='student',
            first_name='Jane',
            last_name='Doe',
            phone_number='1234567891'
        )
        
        with self.assertRaises(Exception):
            Student.objects.create(
                user=user2,
                roll_number='STU001',  # Same roll number
                student_class='10B',
                date_of_birth=date(2005, 3, 20),
                admission_date=date(2020, 6, 1),
                status='active'
            )


class StudentSerializerTest(TestCase):
    """Test cases for Student serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='John',
            last_name='Doe',
            phone_number='1234567890'
        )
        
        self.student = Student.objects.create(
            user=self.user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active'
        )
    
    def test_student_serializer_fields(self):
        """Test student serializer contains expected fields"""
        serializer = StudentSerializer(self.student)
        expected_fields = [
            'id', 'user', 'roll_number', 'student_class',
            'date_of_birth', 'admission_date', 'status', 'assigned_teacher'
        ]
        
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
    
    def test_valid_student_creation(self):
        """Test valid student creation through serializer"""
        data = {
            'user': {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice@test.com',
                'phone_number': '9876543210'
            },
            'roll_number': 'STU002',
            'student_class': '10B',
            'date_of_birth': '2005-03-20',
            'admission_date': '2020-06-01',
            'status': 'active'
        }
        
        serializer = StudentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        
        self.assertEqual(student.roll_number, 'STU002')
        self.assertEqual(student.user.first_name, 'Alice')
        self.assertEqual(student.user.email, 'alice@test.com')
    
    def test_roll_number_validation(self):
        """Test roll number uniqueness validation"""
        data = {
            'user': {
                'first_name': 'Bob',
                'last_name': 'Smith',
                'email': 'bob@test.com',
                'phone_number': '9876543211'
            },
            'roll_number': 'STU001',  # Already exists
            'student_class': '10B',
            'date_of_birth': '2005-03-20',
            'admission_date': '2020-06-01',
            'status': 'active'
        }
        
        serializer = StudentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('roll_number', serializer.errors)
    
    def test_email_validation(self):
        """Test email uniqueness validation"""
        data = {
            'user': {
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'email': 'student@test.com',  # Already exists
                'phone_number': '9876543212'
            },
            'roll_number': 'STU003',
            'student_class': '10B',
            'date_of_birth': '2005-03-20',
            'admission_date': '2020-06-01',
            'status': 'active'
        }
        
        serializer = StudentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_phone_number_validation(self):
        """Test phone number validation"""
        # Test invalid phone number format
        data = {
            'user': {
                'first_name': 'David',
                'last_name': 'Wilson',
                'email': 'david@test.com',
                'phone_number': '123456789'  # Only 9 digits
            },
            'roll_number': 'STU004',
            'student_class': '10B',
            'date_of_birth': '2005-03-20',
            'admission_date': '2020-06-01',
            'status': 'active'
        }
        
        serializer = StudentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
        
        # Test non-numeric phone number
        data['user']['phone_number'] = '123456789a'
        serializer = StudentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)


class StudentViewSetTest(APITestCase):
    """Test cases for StudentViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User',
            phone_number='1111111111'
        )
        
        # Create teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            role='teacher',
            first_name='Teacher',
            last_name='User',
            phone_number='2222222222'
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='Student',
            last_name='User',
            phone_number='3333333333'
        )
        
        # Create teacher instance
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            subject='Mathematics',
            qualification='M.Sc',
            experience_years=5
        )
        
        # Create student instance
        self.student = Student.objects.create(
            user=self.student_user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active',
            assigned_teacher=self.teacher
        )
    
    def test_admin_can_view_all_students(self):
        """Test admin can view all students"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student-list')  # Assuming you have this URL pattern
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_teacher_can_view_assigned_students(self):
        """Test teacher can only view assigned students"""
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('student-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['roll_number'], 'STU001')
    
    def test_student_cannot_access_student_list(self):
        """Test student cannot access student list"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student-list')
        response = self.client.get(url)
        
        # Should return empty queryset or forbidden
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(len(response.data), 0)
    
    def test_admin_can_create_student(self):
        """Test admin can create new student"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student-list')
        
        data = {
            'user': {
                'first_name': 'New',
                'last_name': 'Student',
                'email': 'newstudent@test.com',
                'phone_number': '4444444444'
            },
            'roll_number': 'STU002',
            'student_class': '10B',
            'date_of_birth': '2005-03-20',
            'admission_date': '2020-06-01',
            'status': 'active'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 2)
    
    def test_teacher_cannot_create_student(self):
        """Test teacher cannot create new student"""
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('student-list')
        
        data = {
            'user': {
                'first_name': 'New',
                'last_name': 'Student',
                'email': 'newstudent@test.com',
                'phone_number': '4444444444'
            },
            'roll_number': 'STU002',
            'student_class': '10B',
            'date_of_birth': '2005-03-20',
            'admission_date': '2020-06-01',
            'status': 'active'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access student endpoints"""
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentMeViewTest(APITestCase):
    """Test cases for StudentMeView"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='Student',
            last_name='User',
            phone_number='3333333333'
        )
        
        # Create non-student user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User',
            phone_number='1111111111'
        )
        
        # Create student instance
        self.student = Student.objects.create(
            user=self.student_user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active'
        )
    
    def test_student_can_view_own_profile(self):
        """Test student can view their own profile"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student-me')  # Assuming you have this URL pattern
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['roll_number'], 'STU001')
        self.assertEqual(response.data['user']['first_name'], 'Student')
    
    def test_non_student_cannot_access_student_me(self):
        """Test non-student users cannot access student-me endpoint"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only students can access', response.data['detail'])
    
    def test_student_without_profile_gets_404(self):
        """Test student without profile gets 404"""
        # Create student user without student profile
        user_without_profile = User.objects.create_user(
            username='nostudent@test.com',
            email='nostudent@test.com',
            password='testpass123',
            role='student',
            first_name='No',
            last_name='Student',
            phone_number='5555555555'
        )
        
        self.client.force_authenticate(user=user_without_profile)
        url = reverse('student-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Student profile not found', response.data['detail'])
    
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access student-me endpoint"""
        url = reverse('student-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExportStudentsCSVTest(APITestCase):
    """Test cases for ExportStudentsCSV view"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User',
            phone_number='1111111111'
        )
        
        # Create teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            role='teacher',
            first_name='Teacher',
            last_name='User',
            phone_number='2222222222'
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='Student',
            last_name='User',
            phone_number='3333333333'
        )
        
        # Create teacher instance
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            subject='Mathematics',
            qualification='M.Sc',
            experience_years=5
        )
        
        # Create multiple students
        self.student1 = Student.objects.create(
            user=self.student_user,
            roll_number='STU001',
            student_class='10A',
            date_of_birth=date(2005, 5, 15),
            admission_date=date(2020, 6, 1),
            status='active',
            assigned_teacher=self.teacher
        )
        
        # Create second student
        student_user2 = User.objects.create_user(
            username='student2@test.com',
            email='student2@test.com',
            password='testpass123',
            role='student',
            first_name='Student2',
            last_name='User2',
            phone_number='4444444444'
        )
        
        self.student2 = Student.objects.create(
            user=student_user2,
            roll_number='STU002',
            student_class='10B',
            date_of_birth=date(2005, 3, 20),
            admission_date=date(2020, 6, 1),
            status='inactive'
        )
    
    def test_admin_can_export_csv(self):
        """Test admin can export students CSV"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('export-students-csv')  # Assuming you have this URL pattern
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="students.csv"', response['Content-Disposition'])
        
        # Parse CSV content
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        # Check header
        expected_header = [
            'First Name', 'Last Name', 'Email', 'Phone Number',
            'Roll Number', 'Class', 'Date of Birth',
            'Admission Date', 'Status', 'Assigned Teacher'
        ]
        self.assertEqual(rows[0], expected_header)
        
        # Check data rows (should have 2 students)
        self.assertEqual(len(rows), 3)  # Header + 2 students
    
    def test_csv_content_accuracy(self):
        """Test CSV content contains accurate student data"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('export-students-csv')
        response = self.client.get(url)
        
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        # Check first student data
        student1_row = rows[1]
        self.assertEqual(student1_row[0], 'Student')  # First name
        self.assertEqual(student1_row[1], 'User')     # Last name
        self.assertEqual(student1_row[2], 'student@test.com')  # Email
        self.assertEqual(student1_row[4], 'STU001')   # Roll number
        self.assertEqual(student1_row[5], '10A')      # Class
        self.assertEqual(student1_row[8], 'active')   # Status
        self.assertEqual(student1_row[9], 'Teacher User')  # Assigned teacher
        
        # Check second student data
        student2_row = rows[2]
        self.assertEqual(student2_row[0], 'Student2')
        self.assertEqual(student2_row[4], 'STU002')
        self.assertEqual(student2_row[8], 'inactive')
        self.assertEqual(student2_row[9], 'N/A')  # No assigned teacher
    
    def test_non_admin_cannot_export_csv(self):
        """Test non-admin users cannot export CSV"""
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('export-students-csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test with student user
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot export CSV"""
        url = reverse('export-students-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_empty_csv_export(self):
        """Test CSV export when no students exist"""
        # Delete all students
        Student.objects.all().delete()
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('export-students-csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        # Should only have header row
        self.assertEqual(len(rows), 1)


# Integration tests
class StudentIntegrationTest(APITestCase):
    """Integration tests for student functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User',
            phone_number='1111111111'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            role='teacher',
            first_name='Teacher',
            last_name='User',
            phone_number='2222222222'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            subject='Mathematics',
            qualification='M.Sc',
            experience_years=5
        )
    
    def test_full_student_lifecycle(self):
        """Test complete student lifecycle: create, read, update, delete"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create student
        create_data = {
            'user': {
                'first_name': 'Test',
                'last_name': 'Student',
                'email': 'teststudent@test.com',
                'phone_number': '9999999999'
            },
            'roll_number': 'STU999',
            'student_class': '10A',
            'date_of_birth': '2005-01-01',
            'admission_date': '2020-06-01',
            'status': 'active',
            'assigned_teacher': self.teacher.id
        }
        
        url = reverse('student-list')
        response = self.client.post(url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        student_id = response.data['id']
        
        # Read student
        detail_url = reverse('student-detail', kwargs={'pk': student_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['roll_number'], 'STU999')
        
        # Update student
        update_data = {
            'user': {
                'first_name': 'Updated',
                'last_name': 'Student',
                'email': 'teststudent@test.com',
                'phone_number': '9999999999'
            },
            'roll_number': 'STU999',
            'student_class': '10B',  # Changed class
            'date_of_birth': '2005-01-01',
            'admission_date': '2020-06-01',
            'status': 'active',
            'assigned_teacher': self.teacher.id
        }
        
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_class'], '10B')
        
        # Delete student
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Run tests with: python manage.py test students.tests
# Or with pytest: pytest students/tests.py -v