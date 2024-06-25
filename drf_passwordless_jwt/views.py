from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from drfpasswordless.models import CallbackToken
from drfpasswordless.views import ObtainAuthTokenFromCallbackToken
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .consts import LONG_LIVE_TIME
from .serializers import EmailAuthWhiteListSerializer
from .serializers import JWTSerializer
from .testaccount import exists_test_account
from .testaccount import get_test_account_token
from .utils import generate_jwt


class ObtainEmailTokenView(ObtainEmailCallbackToken):
    serializer_class = EmailAuthWhiteListSerializer

    def post(self, request, *args, **kwargs):
        email = request.data["email"]
        if exists_test_account(email):
            return Response(
                {
                    "detail": f"test account email {email!r} available",
                },
            )

        return super().post(request, *args, **kwargs)


class ObtainJWTView(ObtainAuthTokenFromCallbackToken):
    def post(self, request, *args, **kwargs):
        email = request.data["email"]
        if exists_test_account(email):
            if request.data["token"] == get_test_account_token(email):
                return Response(
                    {
                        "email": email,
                        "token": generate_jwt(email),
                    },
                )

        resp = super().post(request, *args, **kwargs)
        token = generate_jwt(email)
        resp.data["email"] = email
        resp.data["token"] = token

        current_time = timezone.now()
        remove_time = current_time - timedelta(
            seconds=settings.OTP_TOKEN_CLEAN_SECONDS,
        )
        tokens = CallbackToken.objects.filter(created_at__lt=remove_time)
        tokens.delete()

        return resp


class VerifyJWTView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JWTSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if email and exists_test_account(email):
            return Response(
                {
                    "email": email,
                    "exp": LONG_LIVE_TIME,
                },
            )

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=False):
            return Response(
                serializer.validated_data["token"],
                status=status.HTTP_200_OK,
            )

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            headers={"Access-Control-Allow-Origin": "*"},
        )


class VerifyJWTHeaderView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JWTSerializer

    def get(self, request, *args, **kwargs):
        request_method = request.headers.get("X-Forwarded-Method", "")
        if request_method.upper() == "OPTIONS":
            return Response(status=status.HTTP_200_OK)

        email = request.headers.get("x-email")
        if email and exists_test_account(email):
            return Response(
                {
                    "email": email,
                    "exp": LONG_LIVE_TIME,
                },
            )

        auth_header = request.headers.get(settings.AUTH_HEADER_NAME)
        request.headers.get("Cookie")
        auth_cookie = request.COOKIES.get(settings.AUTH_COOKIE_NAME, "")
        if auth_header:
            try:
                _, token = auth_header.split()
            except ValueError:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={
                        "error": "Invalid request,"
                        f" header {settings.AUTH_HEADER_NAME!r}"
                        f" must be provided",
                    },
                    headers={"Access-Control-Allow-Origin": "*"},
                )
        elif auth_cookie:
            token = auth_cookie
        else:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={
                    "error": f"header {settings.AUTH_HEADER_NAME!r} or"
                    f" cookie {settings.AUTH_COOKIE_NAME!r}"
                    "must be provided",
                },
                headers={"Access-Control-Allow-Origin": "*"},
            )

        serializer = self.serializer_class(
            data={"token": token},
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=False):
            return Response(
                serializer.validated_data["token"],
                status=status.HTTP_200_OK,
            )

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            headers={"Access-Control-Allow-Origin": "*"},
        )
