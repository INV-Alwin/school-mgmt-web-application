from rest_framework import serializers
from .models import Exam, Question, StudentExam, StudentAnswer

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'title', 'duration_minutes', 'teacher', 'assigned_students']
        read_only_fields = ['teacher']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'exam', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'question', 'selected_option']


class StudentExamSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True, write_only=True)
    score = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = StudentExam
        fields = ['id', 'student', 'exam', 'start_time', 'end_time', 'score', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        student_exam = StudentExam.objects.create(**validated_data)

        correct_count = 0
        for ans_data in answers_data:
            question = ans_data['question']
            selected = ans_data['selected_option']
            is_correct = question.correct_option == selected
            if is_correct:
                correct_count += 1
            StudentAnswer.objects.create(student_exam=student_exam, **ans_data)

        student_exam.score = correct_count
        student_exam.save()
        return student_exam
