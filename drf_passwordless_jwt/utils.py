from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings


def generate_jwt(email):
    payload = {"email": email}
    exp = timedelta(seconds=settings.JWT_EXPIRE_SECONDS)
    payload['exp'] = datetime.now(tz=timezone.utc) + exp
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def decode_jwt(token):
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    ts = payload['exp']
    payload['exp'] = datetime.fromtimestamp(ts, timezone.utc)
    return payload
