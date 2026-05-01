from django.db.models import Prefetch
from rest_framework import viewsets
from users.models import Shop
from users.serializers import ShopSerializer

from catalog import models as m

from . import serializers as s


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    # lookup_field = "slug"
    serializer_class = s.ProductSerializer

    def get_queryset(self):
        qs = (
            m.Product.objects.select_related(
                "category", "brand", "shop", "product_type"
            )
            .prefetch_related(
                Prefetch(
                    "tags", queryset=m.ProductTag.objects.filter(is_active=True)
                ),
                "attributes",
                "variants__attribute_values",
            )
            .filter(shop__is_active=True)
        )

        brand_slug = self.kwargs.get("brand_slug")

        if brand_slug:
            return qs.filter(brand__slug=brand_slug)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["variants_flag"] = self.request.query_params.get(
            "variants_flag"
        )
        return context


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = s.CategorySerializer

    def get_queryset(self):
        qs = m.Category.objects.all().prefetch_related("children")
        print(self.action)
        if self.action == "list":
            return qs.filter(level=0)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["depth"] = self.request.query_params.get("depth")
        return context


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.Brand.objects.all()
    serializer_class = s.BrandSerializer


class ProductTagViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.ProductTag.objects.all()
    serializer_class = s.ProductTagsSerializer


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class AttributesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.Attribute.objects.all()
    serializer_class = s.AttributesSerializer


class AttributeValuesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.AttributeValue.objects.all()
    serializer_class = s.AttributeValuesSerializer


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.ProductType.objects.all()
    serializer_class = s.ProductTypeSerializer


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = m.ProductVariant.objects.all()
    serializer_class = s.ProductVariantSerializer
