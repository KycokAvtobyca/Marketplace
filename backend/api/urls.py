from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from users.views import SendSMSView

from .views import HybridTokenObtainView

urlpatterns = [
    # path("", include("rest_framework.urls")),
    path("auth/send-sms/", SendSMSView.as_view(), name="send_sms"),
    path(
        "auth/token/", HybridTokenObtainView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("", include("users.urls")),
]
