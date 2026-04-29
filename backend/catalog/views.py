from django.db.models import Prefetch
from rest_framework import viewsets

from catalog.models import Category, Product, ProductTag

from .serializers import (
    CategorySerializer,
    ProductSerializer,
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = (
        Product.objects.select_related(
            "category", "brand", "shop", "product_type"
        )
        .prefetch_related(
            Prefetch(
                "tags", queryset=ProductTag.objects.filter(is_active=True)
            ),
            "attributes",
            "variants__attribute_values",
        )
        .filter(shop__is_active=True)
    )
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.all().prefetch_related("children")
        print(self.action)
        if self.action == "list":
            return qs.filter(level=0)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["depth"] = self.request.query_params.get("depth")
        return context
