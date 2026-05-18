from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderCreateView, OrderViewSet, PickupPointListView

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")

urlpatterns = [
    path("pickup-points/", PickupPointListView.as_view(), name="pickup_points"),
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("", include(router.urls)),
]
