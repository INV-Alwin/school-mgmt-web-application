from rest_framework import serializers
from .models import Student
from users.models import User
from users.serializers import UserSerializer  

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'roll_number', 'student_class',
            'date_of_birth', 'admission_date', 'status', 'assigned_teacher'
        ]

    def validate_roll_number(self, value):
        if Student.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("Roll number must be unique.")
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
            password='student@123',
            role='student',
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data['phone_number']
        )

        student = Student.objects.create(user=user, **validated_data)
        return student
