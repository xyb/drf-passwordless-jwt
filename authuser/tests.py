import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user("xyb@test.com", "password")

        self.assertTrue(isinstance(user, User))

    def test_create_user_no_email(self):
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user("")

        assert str(excinfo.value) == "The given email must be set"

    def test_create_super_user(self):
        user = User.objects.create_superuser("xyb@test.com", "password")

        self.assertTrue(isinstance(user, User))
