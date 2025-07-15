from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, QuestionViewSet, AssignedExamsView, SubmitExamView

router = DefaultRouter()
router.register(r'exams', ExamViewSet)
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('assigned/', AssignedExamsView.as_view(), name='assigned-exams'),
    path('submit/', SubmitExamView.as_view(), name='submit-exam'),
    path('', include(router.urls)),
]
