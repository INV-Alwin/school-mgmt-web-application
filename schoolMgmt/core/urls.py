from django.urls import path, include
from rest_framework.routers import DefaultRouter
from teachers.views import TeacherViewSet,ExportTeachersCSV,ImportTeachersCSV
from students.views import ExportStudentsCSV, StudentViewSet, StudentMeView, ImportStudentsCSV

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('students/me/', StudentMeView.as_view(), name='student-me'),
    path('teachers/export/', ExportTeachersCSV.as_view(), name='export-teachers'),
    path('students/export/', ExportStudentsCSV.as_view(), name='export-students'),
    path('teachers/import/', ImportTeachersCSV.as_view(), name='import-teachers'),
    path('students/import/', ImportStudentsCSV.as_view(), name='import-students'),
    path('', include(router.urls)),
]
