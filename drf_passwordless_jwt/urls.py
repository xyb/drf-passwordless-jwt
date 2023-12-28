"""drf_passwordless_jwt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drfpasswordless.settings import api_settings

from .views import ObtainEmailTokenView
from .views import ObtainJWTView
from .views import VerifyJWTHeaderView
from .views import VerifyJWTView

urlpatterns = [
    path(
        api_settings.PASSWORDLESS_AUTH_PREFIX,
        VerifyJWTView.as_view(),
        name="verify_jwt_token",
    ),
    path(
        api_settings.PASSWORDLESS_AUTH_PREFIX + "jwt/",
        ObtainJWTView.as_view(),
        name="auth_jwt_token",
    ),
    path(
        api_settings.PASSWORDLESS_AUTH_PREFIX + "email/",
        ObtainEmailTokenView.as_view(),
        name="auth_email_token",
    ),
    path(
        api_settings.PASSWORDLESS_AUTH_PREFIX + "header/",
        VerifyJWTHeaderView.as_view(),
        name="verify_jwt_token_header",
    ),
    path("admin/", admin.site.urls),
]
