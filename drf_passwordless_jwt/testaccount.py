from os import getenv

from django.conf import settings


def get_test_account_token(email):
    name = email.replace("@", "_at_").replace(".", "_")
    env = f"{settings.EMAIL_TEST_ACCOUNT_PREFIX}{name}"
    return getenv(env)


def exists_test_account(email):
    return bool(get_test_account_token(email))
