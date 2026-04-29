from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import HybridTokenObtainView, ProfileView, SendSMSView

urlpatterns = [
    path("auth/send-sms/", SendSMSView.as_view(), name="send_sms"),
    path(
        "auth/token/", HybridTokenObtainView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
