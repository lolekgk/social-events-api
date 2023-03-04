from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.registration.views import (
    ConfirmEmailView,
    RegisterView,
    VerifyEmailView,
)
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenVerifyView

app_name = "authentication"

urlpatterns = [
    # dj-rest-auth endpoints
    path("account-confirm-email/<str:key>/", ConfirmEmailView.as_view()),
    path("register/", RegisterView.as_view()),
    path(
        "verify-email/",
        VerifyEmailView.as_view(),
        name="verify_email",
    ),
    path(
        "account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    re_path(
        r"^account-confirm-email/(?P<key>[-:\w]+)/$",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password/reset/",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="password_change",
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "token/refresh/",
        get_refresh_view().as_view(),
        name="token_refresh",
    ),
]
