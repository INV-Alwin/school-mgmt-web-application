from django.test import TestCase
from users.models import User
from users.serializers import UserSerializer

class UserSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='1234567890',
            role=User.Role.STUDENT
        )

    def test_user_serializer_valid_data(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['phone_number'], '1234567890')

    def test_user_serializer_input(self):
        input_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'phone_number': '0987654321',
        }
        serializer = UserSerializer(data=input_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'new@example.com')
