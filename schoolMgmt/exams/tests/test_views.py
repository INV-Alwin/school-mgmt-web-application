from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from users.models import User
from teachers.models import Teacher
from students.models import Student
from exams.models import Exam, StudentExam, Question
from django.utils import timezone

class ExamViewSetTest(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='admin'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='teacher123',
            role='teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T101',
            phone='9876543210',
            subject_specialization='Math',
            date_of_joining='2022-06-01',
            status='active'
        )

        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='student123',
            role='student'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            roll_number='S101',
            student_class='10',
            date_of_birth='2008-05-12',
            admission_date='2023-06-15',
            status='Active'
        )

        self.exam = Exam.objects.create(
            title="Math Exam",
            duration_minutes=30,
            teacher=self.teacher,
        )
        self.exam.assigned_students.add(self.student)

    def test_create_exam(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            'title': 'Science Exam',
            'duration_minutes': 45,
            'teacher': self.teacher.id
        }
        url = reverse('exam-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 2)

    def test_list_exams_as_teacher(self):
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('exam-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_exams_as_student(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse('assigned-exams')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_submit_exam(self):
        self.client.force_authenticate(user=self.student_user)
        data = {
            'exam': self.exam.id,
            'answers': [
                {'question': 1, 'selected_option': 'A'},
                {'question': 2, 'selected_option': 'B'}
            ]
        }
        url = reverse('submit-exam')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submit_exam_time_exceeded(self):
        # Manipulate the exam time to simulate exceeding the time limit
        self.exam.duration_minutes = 1
        self.exam.save()
        self.client.force_authenticate(user=self.student_user)
        data = {
            'exam': self.exam.id,
            'answers': [
                {'question': 1, 'selected_option': 'A'},
                {'question': 2, 'selected_option': 'B'}
            ]
        }
        url = reverse('submit-exam')
        # Simulating end time passed
        timezone.now = lambda: timezone.now() + timezone.timedelta(minutes=2)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Exam time exceeded. Submission rejected.')

class QuestionViewSetTest(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='admin'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='teacher123',
            role='teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T101',
            phone='9876543210',
            subject_specialization='Math',
            date_of_joining='2022-06-01',
            status='active'
        )

        self.exam = Exam.objects.create(
            title="Math Exam",
            duration_minutes=30,
            teacher=self.teacher,
        )

    def test_create_question(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            'exam': self.exam.id,
            'question_text': 'What is 2 + 2?',
            'option_a': '3',
            'option_b': '4',
            'option_c': '5',
            'option_d': '6',
            'correct_option': 'B'
        }
        url = reverse('question-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_question_limit(self):
        # Add 5 questions already
        for i in range(5):
            Question.objects.create(
                exam=self.exam,
                question_text=f'Question {i+1}',
                option_a=f'Option {i+1}',
                option_b='Option 2',
                option_c='Option 3',
                option_d='Option 4',
                correct_option='A'
            )

        self.client.force_authenticate(user=self.teacher_user)
        data = {
            'exam': self.exam.id,
            'question_text': 'What is 5 + 5?',
            'option_a': '10',
            'option_b': '11',
            'option_c': '12',
            'option_d': '13',
            'correct_option': 'A'
        }
        url = reverse('question-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Maximum 5 questions allowed')
