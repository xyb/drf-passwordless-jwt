import os
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


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
        self.assertEqual(msg.subject, 'Your Login Token')
        self.assertTrue(msg.body.startswith('Enter this token to sign in:'))
        token = msg.body.split()[-1]
        self.assertEqual(len(token), 6)
        self.assertTrue(token.isdigit())
        self.assertEqual(msg.from_email, 'xyb@mydomain.com')
        self.assertEqual(msg.to, ['xyb@test.com'])

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_auth_jwt_token(self):
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "a@a.com", "token": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ['email', 'token'])
        self.assertEqual(json['email'], 'a@a.com')

    @patch.dict(os.environ, {"EMAIL_TEST_ACCOUNT_a_at_a_com": "123456"})
    def test_verify_jwt_token(self):
        response = self.client.post(
            reverse("auth_jwt_token"),
            {"email": "a@a.com", "token": "123456"},
            format="json",
        )
        token = response.json()['token']

        response = self.client.post(
            reverse("verify_jwt_token"),
            {"token": token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(list(json.keys()), ['email', 'exp'])
        self.assertEqual(json['email'], 'a@a.com')
