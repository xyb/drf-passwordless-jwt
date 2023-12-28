import os
import re
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .serializers import EmailAuthWhiteListSerializer


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_WHITE_LIST=r"^.*@test.com",
)
class TaskTest(APITestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_token_email(self):
        response = self.client.post(
            reverse("auth_email_token"),
            {"email": "xyb@test.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"detail": "A login token has been sent to your email."},
        )
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, "Your Login Token")
        self.assertTrue(msg.body.startswith("Enter this token to sign in:"))
        token = msg.body.split()[-1]
        self.assertEqual(len(token), 6)
        self.assertTrue(token.isdigit())
        self.assertEqual(msg.from_email, "xyb@mydomain.com")
        self.assertEqual(msg.to, ["xyb@test.com"])

    def test_invalid_email(self):
        # monkey patch white list setting
        EmailAuthWhiteListSerializer.email_regex.regex = re.compile(r"^.*@test.com")

        response = self.client.post(
            reverse("auth_email_token"),
            {"email": "a@invalid.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"email": ["email address not in white list"]},
        )
        self.assertEqual(len(mail.outbox), 0)

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_obtain_jwt_test_account(self):
        response = self.client.post(
            reverse("auth_email_token"),
            {"email": "a@a.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ["detail"])
        self.assertEqual(json["detail"], "test account email 'a@a.com' available")

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_auth_jwt_token(self):
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "a@a.com", "token": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ["email", "token"])
        self.assertEqual(json["email"], "a@a.com")

    def test_invalid_login_token(self):
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "a@test.com", "token": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"token": ["The token you entered isn't valid."]},
        )

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_verify_jwt_token(self):
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "a@a.com", "token": "123456"},
            format="json",
        )
        token = response.json()["token"]

        response = self.client.post(
            reverse("verify_jwt_token"),
            {"token": token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ["email", "exp"])
        self.assertEqual(json["email"], "a@a.com")

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_verify_jwt_token_test_account(self):
        response = self.client.post(
            reverse("verify_jwt_token"),
            {"email": "a@a.com", "token": "anything"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ["email", "exp"])
        self.assertEqual(json["email"], "a@a.com")

    def test_invalid_jwt_token(self):
        response = self.client.post(
            reverse("verify_jwt_token"),
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJzdWIiOiIxMjM0NTY3ODkwIiwiZW1haWwiOiJhQGEuY29tIiwiaWF0IjoxNTE2MjM5MDIyfQ."
                "mmqUsu7kpT7M9QUYj69X1TNVCyatAPgky9JXtrSuHrU",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_format_jwt_token(self):
        response = self.client.post(
            reverse("verify_jwt_token"),
            {"token": "abc"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_verify_jwt_token_header(self):
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "a@a.com", "token": "123456"},
            format="json",
        )
        token = response.json()["token"]

        response = self.client.post(
            reverse("verify_jwt_token_header"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ["email", "exp"])
        self.assertEqual(json["email"], "a@a.com")

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_verify_jwt_token_header_test_account(self):
        response = self.client.post(
            reverse("verify_jwt_token_header"),
            HTTP_AUTHORIZATION="Bearer anything",
            HTTP_EMAIL="a@a.com",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ["email", "exp"])
        self.assertEqual(json["email"], "a@a.com")

    def test_invalid_jwt_token_header(self):
        response = self.client.post(
            reverse("verify_jwt_token_header"),
            HTTP_AUTHORIZATION="Bearer badbeef",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_format_jwt_token_header(self):
        response = self.client.post(
            reverse("verify_jwt_token_header"),
            HTTP_AUTHORIZATION="badbeef",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_jwt_token_header(self):
        response = self.client.post(
            reverse("verify_jwt_token_header"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_obtain_jwt(self):
        response = self.client.post(
            reverse("auth_email_token"),
            {"email": "xyb@test.com"},
            format="json",
        )
        msg = mail.outbox[0]
        token = msg.body.split()[-1]
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "xyb@test.com", "token": token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(set(json.keys()), {"email", "token"})
        self.assertEqual(json["email"], "xyb@test.com")
