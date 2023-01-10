from django.conf import settings
from django.core.validators import RegexValidator
from drfpasswordless.serializers import EmailAuthSerializer
from rest_framework import serializers

from .utils import decode_jwt


class EmailAuthWhiteListSerializer(EmailAuthSerializer):
    email_regex = RegexValidator(
        regex=settings.EMAIL_WHITE_LIST,
        message=settings.EMAIL_WHITE_LIST_MESSAGE,
    )
    email = serializers.EmailField(validators=[email_regex])


class JWTSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            value = decode_jwt(value)
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('token expired')
        return value
