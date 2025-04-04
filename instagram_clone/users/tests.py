from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class ProfileSignalTest(TestCase):
    def test_profile_creation(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.assertTrue(Profile.objects.filter(user=user).exists())
