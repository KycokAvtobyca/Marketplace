from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)

from .views import (
    AdminAutoLoginView,
    CreateShopView,
    DeleteShopRequestView,
    HttpOnlyTokenRefreshView,
    HybridTokenObtainView,
    LogoutView,
    MyShopView,
    PhoneChangeView,
    ProfileView,
    SendSMSView,
    ShopReportOptionsView,
    ShopViewSet,
)

router = DefaultRouter()
router.register("shop", ShopViewSet)

urlpatterns = [
    path("auth/send-sms/", SendSMSView.as_view(), name="send_sms"),
    path(
        "auth/token/", HybridTokenObtainView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/",
        HttpOnlyTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/phone-change/", PhoneChangeView.as_view(), name="phone_change"),
    path("shop/create/", CreateShopView.as_view(), name="shop_create"),
    path("shop/delete-request/", DeleteShopRequestView.as_view(), name="shop_delete_request"),
    path("shop/my/", MyShopView.as_view(), name="my_shop"),
    path("shop/report-options/", ShopReportOptionsView.as_view(), name="shop_report_options"),
    path("admin-login/", AdminAutoLoginView.as_view(), name="admin_login"),
    path("", include(router.urls)),
]
