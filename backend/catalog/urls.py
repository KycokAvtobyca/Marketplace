from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from catalog import views as v

router = DefaultRouter()
router.register("categories", v.CategoryViewSet, basename="category")
router.register("products", v.ProductViewSet, basename="product")
router.register(
    "product-catalog", v.ProductCatalogViewSet, basename="product-catalog"
)
router.register("brands", v.BrandViewSet)
router.register("product-tags", v.ProductTagViewSet)
router.register("attributes", v.AttributesViewSet)
router.register("attribute-values", v.AttributeValuesViewSet)
router.register("product-types", v.ProductTypeViewSet)
router.register("sku", v.ProductVariantViewSet, basename="sku")
router.register("filters", v.FiltersViewSet, basename="catalog")


# Вложенные роутеры
brands_router = routers.NestedSimpleRouter(router, "brands", lookup="brand")
brands_router.register("products", v.ProductViewSet, basename="brand-product")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(brands_router.urls)),
    path("filter-price/", v.PriceRangeAPIView.as_view(), name="filter-price"),
]
