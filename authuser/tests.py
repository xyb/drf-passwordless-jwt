import pytest
from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase

from .models import User


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

    @pytest.mark.xfail
    def test_create_user_django(self):
        user = DjangoUser.objects.create_user("xyb@test.com", "password")

        self.assertTrue(isinstance(user, User))
