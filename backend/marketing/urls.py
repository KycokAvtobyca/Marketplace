from rest_framework.routers import DefaultRouter

from .views import DiscountViewSet, PromoCodeViewSet

router = DefaultRouter()
router.register("discounts", DiscountViewSet, basename="discount")
router.register("promocodes", PromoCodeViewSet, basename="promocode")

urlpatterns = router.urls
