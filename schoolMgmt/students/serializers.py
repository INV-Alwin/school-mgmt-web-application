from rest_framework import serializers
from .models import Student
from users.models import User

class StudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'roll_number', 'class_name', 'date_of_birth', 'admission_date',
            'status', 'assigned_teacher'
        ]

    def validate_roll_number(self, value):
        if Student.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("Roll number must be unique.")
        return value

    def validate_email(self, value):
        email = value.get('email') if isinstance(value, dict) else value
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already in use.")
        return value
    
    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits.")
        return value


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['email'],
            email=user_data['email'],
            password="student@123",
            role='student'
        )
        student = Student.objects.create(user=user, **validated_data)
        return student
