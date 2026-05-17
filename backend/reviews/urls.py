from rest_framework.routers import DefaultRouter

from .views import (
    ProductComplaintViewSet,
    ProductQuestionViewSet,
    ReviewComplaintViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register("product-complaints", ProductComplaintViewSet, basename="product-complaint")
router.register("review-complaints", ReviewComplaintViewSet, basename="review-complaint")
router.register("questions", ProductQuestionViewSet, basename="product-question")
router.register("", ReviewViewSet, basename="review")

urlpatterns = router.urls
