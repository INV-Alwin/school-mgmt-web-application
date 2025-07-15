from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from exams.models import Exam, Question, StudentExam
from .serializers import ExamSerializer, QuestionSerializer, StudentExamSerializer
from users.permissions import IsAdminOrTeacherReadOnly,IsAdminOrTeacher,IsStudent
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from teachers.models import Teacher
from rest_framework.decorators import action
from exams.models import Exam
from rest_framework.exceptions import ValidationError


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrTeacher]

    def perform_create(self, serializer):
        try:
            teacher_instance = self.request.user.teacher
        except Teacher.DoesNotExist:
            raise PermissionDenied("This user is not registered as a teacher.")
        
        serializer.save(teacher=teacher_instance)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Question.objects.filter(exam__teacher=self.request.user)

    def perform_create(self, serializer):
        exam = serializer.validated_data['exam']
        if exam.teacher != self.request.user:
            raise PermissionDenied("You are not the teacher of this exam.")
        if exam.questions.count() >= 5:
            raise ValidationError("Maximum 5 questions allowed.")
        serializer.save()

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Expected a list of questions."}, status=400)

        
        if len(data) > 5:
            return Response({"error": "Only 5 questions allowed per exam."}, status=400)

        serializer = QuestionSerializer(data=data, many=True, context={'request': request})

        if serializer.is_valid():
            exam_ids = set(q["exam"] for q in data)
            if len(exam_ids) != 1:
                return Response({"error": "All questions must belong to the same exam."}, status=400)

            exam = Exam.objects.get(id=list(exam_ids)[0])
            if exam.teacher.user != request.user:
                return Response({"error": "You can only add questions to your own exams."}, status=403)

            existing_count = exam.questions.count()
            if existing_count + len(data) > 5:
                return Response({"error": f"Only {5 - existing_count} more question(s) allowed for this exam."}, status=400)

            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class AssignedExamsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        if request.user.role != 'student':
            return Response({'error': 'Only students can view assigned exams'}, status=403)

        try:
            student = request.user.student
        except:
            return Response({'error': 'Student profile not found'}, status=404)

        exams = Exam.objects.filter(assigned_students=student)
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

class SubmitExamView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        if request.user.role != 'student':
            return Response({'error': 'Only students can submit exams'}, status=403)

        try:
            student = request.user.student
        except:
            return Response({'error': 'Student profile not found'}, status=404)

        serializer = StudentExamSerializer(data=request.data)
        if serializer.is_valid():
            exam = serializer.validated_data['exam']
            start_time = serializer.validated_data.get('start_time', timezone.now())
            allowed_end_time = start_time + timezone.timedelta(minutes=exam.duration_minutes)

            if timezone.now() > allowed_end_time:
                return Response({'error': 'Exam time exceeded. Submission rejected.'}, status=400)

            serializer.save(
                student=student,
                start_time=start_time,
                end_time=timezone.now()
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


