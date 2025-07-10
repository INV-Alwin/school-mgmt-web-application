from rest_framework import serializers
from .models import Teacher
from users.models import User

class TeacherSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'subject_specialization', 'employee_id', 'date_of_joining', 'status'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['email'],  # can use email as username
            email=user_data['email'],
            password="teacher@123",       # set default password (should force change)
            role='teacher'
        )
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher
