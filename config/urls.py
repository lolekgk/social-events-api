"""config URL Configuration

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
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    # apps endpoints
    # path('messagebox/', include('messagebox.urls')),
    # path('users/', include('users.urls')),
    path("admin/", admin.site.urls),
    path("events/", include("events.urls")),
    # dj-rest-auth endpoints
    path(
        "auth/register/",
        include("dj_rest_auth.registration.urls"),
    ),
    path("auth/login/", LoginView.as_view(), name="rest_login"),
    path("auth/logout/", LogoutView.as_view(), name="rest_logout"),
    path(
        "auth/password/reset/",
        PasswordResetView.as_view(),
        name="rest_password_reset",
    ),
    path(
        "auth/password/reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path(
        "auth/password/change/",
        PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "auth/token/refresh/",
        get_refresh_view().as_view(),
        name="token_refresh",
    ),
    # swagger endpoints
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redocs/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# django-recurrence
# jsi18n can be anything you like here
js_info_dict = {
    "packages": ("recurrence",),
}
urlpatterns += [
    re_path(r"^jsi18n/$", JavaScriptCatalog.as_view(), js_info_dict),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
