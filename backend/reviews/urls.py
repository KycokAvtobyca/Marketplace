from rest_framework.routers import DefaultRouter

from .views import ProductQuestionViewSet, ReviewViewSet

router = DefaultRouter()
router.register("questions", ProductQuestionViewSet, basename="product-question")
router.register("", ReviewViewSet, basename="review")

urlpatterns = router.urls
