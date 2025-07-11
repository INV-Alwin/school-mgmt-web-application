from django.urls import path, include
from rest_framework.routers import DefaultRouter
from teachers.views import TeacherViewSet,ExportTeachersCSV
from students.views import ExportStudentsCSV, StudentViewSet, StudentMeView

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('students/me/', StudentMeView.as_view(), name='student-me'),
    path('teachers/export/', ExportTeachersCSV.as_view(), name='export-teachers'),
    path('students/export/', ExportStudentsCSV.as_view(), name='export-students'),
    path('', include(router.urls)),
]
