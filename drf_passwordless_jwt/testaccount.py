from django.conf import settings
from os import getenv

def get_test_account_token(email):
    name = email.replace('@', '_at_').replace('.', '_')
    env = '{}{}'.format(settings.EMAIL_TEST_ACCOUNT_PREFIX, name)
    return getenv(env)


def exists_test_account(email):
    return bool(get_test_account_token(email))
