from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from drfpasswordless.models import CallbackToken
from drfpasswordless.views import (ObtainAuthTokenFromCallbackToken,
                                   ObtainEmailCallbackToken)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import generate_jwt
from .serializers import EmailAuthWhiteListSerializer, JWTSerializer
from .testaccount import get_test_account_token, exists_test_account


class ObtainEmailTokenView(ObtainEmailCallbackToken):
    serializer_class = EmailAuthWhiteListSerializer
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        if exists_test_account(email):
            return Response({'detail':
                             f'test account email {email!r} available'})

        return super(ObtainEmailTokenView, self).post(request, *args, **kwargs)


class ObtainJWTView(ObtainAuthTokenFromCallbackToken):
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        if exists_test_account(email):
            if request.data['token'] == get_test_account_token(email):
                return Response({
                    'email': email,
                    'token': generate_jwt(email),
                })

        resp = super(ObtainJWTView, self).post(request, *args, **kwargs)
        token = generate_jwt(email)
        resp.data['email'] = email
        resp.data['token'] = token

        current_time = timezone.now()
        remove_time = current_time - timedelta(
            seconds=settings.OTP_TOKEN_CLEAN_SECONDS)
        tokens = CallbackToken.objects.filter(created_at__lt=remove_time)
        tokens.delete()

        return resp


class VerifyJWTView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JWTSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email and exists_test_account(email):
            return Response({
                'email': email,
                'exp': '9999-12-31T23:59:59',
            })

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=False):
            return Response(
                serializer.validated_data['token'],
                status=status.HTTP_200_OK,
            )

        return Response(status=status.HTTP_401_UNAUTHORIZED)
