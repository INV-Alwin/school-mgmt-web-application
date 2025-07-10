from django.urls import path, include
from rest_framework.routers import DefaultRouter
from teachers.views import TeacherViewSet
from students.views import StudentViewSet, StudentMeView

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('me/', StudentMeView.as_view(), name='student-me'),
    path('', include(router.urls)),
]
