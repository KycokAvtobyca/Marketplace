from django.db.models import Max, Min, Prefetch
from rest_framework import views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from users import models as mu

from catalog import models as m
from catalog.mixins import CategoryTreeOptimizerMixin

from . import serializers as s
from .pagination import DefaultCursorPagination, FilterValuesPagination
from .utils import get_limited_data


class ProductViewSet(CategoryTreeOptimizerMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = s.ProductSerializer
    pagination_class = DefaultCursorPagination

    def get_queryset(self):

        variants_flag = self.request.query_params.get("variants_flag")

        prefetches = [
            Prefetch(
                "tags", queryset=m.ProductTag.objects.filter(is_active=True)
            ),
            Prefetch(
                "attributes",
                queryset=m.Attribute.objects.filter(is_active=True),
            ),
        ]

        if variants_flag:
            prefetches.append(
                Prefetch(
                    "variants",
                    queryset=m.ProductVariant.objects.filter(
                        is_active=True
                    ).prefetch_related("attribute_values"),
                )
            )

        qs = (
            m.Product.objects.select_related(
                "brand",
                "shop",
                "product_type",
                "category",  # доступ к category_id без запроса
            )
            .prefetch_related(*prefetches)
            .filter(shop__is_active=True)
        )

        brand_slug = self.kwargs.get("brand_slug")

        if brand_slug:
            return qs.filter(brand__slug=brand_slug)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "variants_flag": self.request.query_params.get("variants_flag"),
                "depth": self.request.query_params.get("depth"),
            }
        )
        return context


class CategoryViewSet(
    CategoryTreeOptimizerMixin, viewsets.ReadOnlyModelViewSet
):
    lookup_field = "slug"
    serializer_class = s.CategorySerializer
    pagination_class = FilterValuesPagination
    category_relation_path = ""

    def get_queryset(self):
        # убрали .prefetch_related("children"), так как миксин сделает это эффективнее
        qs = m.Category.objects.all()
        if (
            self.action == "list"
            or self.request.query_params.get("depth") == "0"
        ):
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
    pagination_class = FilterValuesPagination


class ProductTagViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.ProductTag.objects.all()
    serializer_class = s.ProductTagsSerializer
    pagination_class = DefaultCursorPagination


class AttributesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.Attribute.objects.all()
    serializer_class = s.AttributesSerializer
    pagination_class = FilterValuesPagination


class AttributeValuesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = m.AttributeValue.objects.all()
    serializer_class = s.AttributeValuesSerializer
    pagination_class = DefaultCursorPagination


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = m.ProductType.objects.all()
    serializer_class = s.ProductTypeSerializer
    pagination_class = FilterValuesPagination


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.ProductVariantSerializer
    pagination_class = DefaultCursorPagination

    def get_queryset(self):
        user = self.request.user

        return (
            m.ProductVariant.objects.with_prices(user=user)
            .prefetch_related("attribute_values")
            .filter(is_active=True)
        )


class PriceRangeAPIView(views.APIView):
    def get(self, request: Request):
        user = request.user

        prices = m.ProductVariant.objects.with_prices(user=user).aggregate(
            min_price=Min("discounted_price"), max_price=Max("discounted_price")
        )

        return Response(
            {"min": prices["min_price"] or 0, "max": prices["max_price"] or 0}
        )


class FilterViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"])
    def categories(self, request: Request, *args, **kwargs):
        params = request._request.GET.copy()

        # По умолчанию ставим уровень вложенности 3
        params["depth"] = 3

        request._request.GET = params

        category_list_view = CategoryViewSet.as_view({"get": "list"})

        return category_list_view(request._request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def types(self, request: Request, *args, **kwargs):
        # Собираем значения query param categories
        categories = request.query_params.getlist("categories")
        print(categories)

        if not categories or len(categories) < 1 or categories[0] == "/":
            raise ValidationError(
                {
                    "categories": "Нужно передать 1 или более категорий для продолжения фильтрации"
                }
            )

        qs = m.ProductType.objects.filter(
            products__category__slug__in=categories
        ).distinct()

        product_type_list_view = ProductTypeViewSet.as_view(
            {"get": "list"}, queryset=qs
        )

        return product_type_list_view(request._request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def meta(self, request: Request, *args, **kwargs):
        categories = request.query_params.getlist("categories")
        types = request.query_params.getlist("types")

        if not categories or len(categories) < 1 or categories[0] == "/":
            raise ValidationError(
                {
                    "categories": "Нужно передать 1 или более категорий для продолжения фильтрации"
                }
            )

        if not types or len(types) < 1 or types[0] == "/":
            raise ValidationError(
                {
                    "types": "Нужно передать 1 или более типов продукта для продолжения фильтрации"
                }
            )

        # def get_paginated_data(qs, serializer_class):
        #     page = paginator.paginate_queryset(qs, request)
        #     serializer = serializer_class(
        #         page, many=True, context={"request": request}
        #     )

        #     return {
        #         "next": paginator.get_next_link(),
        #         "previous": paginator.get_previous_link(),
        #         "results": serializer.data,
        #     }

        qs = m.Product.objects.filter(
            category__slug__in=categories, product_type__slug__in=types
        ).distinct()

        brands = m.Brand.objects.filter(products__in=qs).distinct()
        shops = mu.Shop.objects.filter(products__in=qs).distinct()
        attributes = (
            m.Attribute.objects.filter(products__in=qs)
            .distinct()
            .prefetch_related("attribute_values")
        )

        data = {
            "brands": get_limited_data(
                request, brands, s.BrandSerializer, "brands"
            ),
            "shops": get_limited_data(
                request, shops, s.ShopSerializer, "shops"
            ),
            "attributes": get_limited_data(
                request, attributes, s.AttributesSerializer, "attributes"
            ),
        }

        return Response(data)


# class FiltersApiView(views.APIView):
#     """
#     Эндпоинт для получения всех данных для модалки фильтров
#     """
#     # category:
#     #     Категории:
#     #     ...
#         #     producttype:
#             #     Типы продукта:
#             #     ...
#                 #     brand: брэнды
#                 #     shop: магазин
#                 #     attributes Атрибуты:
#                       # attribute_values значения атрибутов
#                       # ...
#                 #     Цена

#     def get(self, request):
#         paginator = FilterValuesPagination()

#         # Бренды с пагинацией
#         brands_qs = m.Brand.objects.all()
#         brands_page = paginator.paginate_queryset(brands_qs, request)
#         brands_data = s.BrandSerializer(brands_page,)
