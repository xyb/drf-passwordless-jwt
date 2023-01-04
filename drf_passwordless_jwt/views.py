from datetime import timedelta

import jwt
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from drfpasswordless.models import CallbackToken
from drfpasswordless.serializers import EmailAuthSerializer
from drfpasswordless.views import (ObtainAuthTokenFromCallbackToken,
                                   ObtainEmailCallbackToken)
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import decode_jwt, generate_jwt


class EmailAuthWhiteListSerializer(EmailAuthSerializer):
    email_regex = RegexValidator(
        regex=settings.EMAIL_WHITE_LIST,
        message=settings.EMAIL_WHITE_LIST_MESSAGE,
    )
    email = serializers.EmailField(validators=[email_regex])


class ObtainEmailWhiteListCallbackToken(ObtainEmailCallbackToken):
    serializer_class = EmailAuthWhiteListSerializer


class ObtainJWTFromCallbackToken(ObtainAuthTokenFromCallbackToken):
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        resp = super(ObtainJWTFromCallbackToken, self).post(request, *args,
                                                            **kwargs)
        token = generate_jwt(email)
        resp.data['email'] = email
        resp.data['token'] = token

        current_time = timezone.now()
        remove_time = current_time - timedelta(
            seconds=settings.OTP_TOKEN_CLEAN_SECONDS)
        tokens = CallbackToken.objects.filter(created_at__lt=remove_time)
        tokens.delete()

        return resp


class JWTSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            value = decode_jwt(value)
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('token expired')
        return value


class VerifyJWT(APIView):
    permission_classes = [AllowAny]
    serializer_class = JWTSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=False):
            return Response(
                serializer.validated_data['token'],
                status=status.HTTP_200_OK,
            )

        return Response(status=status.HTTP_401_UNAUTHORIZED)
