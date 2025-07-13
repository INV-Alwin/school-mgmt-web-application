from django.test import TestCase
from django.utils import timezone
from students.models import Student
from users.models import User
from teachers.models import Teacher

class StudentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='studentuser',
            password='pass123',
            first_name='John',
            last_name='Doe'
        )

        self.teacher_user = User.objects.create_user(
            username='teacheruser',
            password='pass123',
            first_name='Jane',
            last_name='Smith'
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            subject_specialization='Mathematics',
            employee_id='EMP123',
            date_of_joining='2023-01-01',
            status='Active'
        )

        self.student = Student.objects.create(
            user=self.user,
            roll_number='ROLL001',
            student_class='10A',
            date_of_birth='2005-06-15',
            admission_date='2020-04-01',
            status='active',
            assigned_teacher=self.teacher
        )

    def test_student_creation(self):
        self.assertEqual(self.student.roll_number, 'ROLL001')
        self.assertEqual(self.student.student_class, '10A')
        self.assertEqual(self.student.status, 'active')
        self.assertEqual(self.student.assigned_teacher, self.teacher)
        self.assertEqual(self.student.user.username, 'studentuser')

    def test_string_representation(self):
        expected_str = "John Doe (ROLL001)"
        self.assertEqual(str(self.student), expected_str)

    def test_assigned_teacher_optional(self):
        student_no_teacher = Student.objects.create(
            user=User.objects.create_user(username='no_teacher'),
            roll_number='ROLL002',
            student_class='9B',
            date_of_birth='2006-05-10',
            admission_date='2021-06-01',
            status='inactive'
            # no teacher assigned
        )
        self.assertIsNone(student_no_teacher.assigned_teacher)
