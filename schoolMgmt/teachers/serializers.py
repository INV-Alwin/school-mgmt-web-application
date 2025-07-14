from rest_framework import serializers
from .models import Teacher
from users.models import User
from users.serializers import UserSerializer

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'subject_specialization',
            'employee_id', 'date_of_joining', 'status'
        ]

    def validate_employee_id(self, value):
        if Teacher.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID must be unique.")
        return value

    def validate(self, attrs):
        user_data = attrs.get("user", {})
        email = user_data.get("email")
        phone = user_data.get("phone_number")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already in use."})

        if not phone.isdigit() or len(phone) != 10:
            raise serializers.ValidationError({"phone_number": "Phone number must be 10 digits."})

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['email'],
            email=user_data['email'],
            password='teacher@123',
            role='teacher',
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data['phone_number']
        )
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher
