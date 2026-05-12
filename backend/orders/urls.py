from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderCreateView, OrderViewSet

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")

urlpatterns = [
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("", include(router.urls)),
]
