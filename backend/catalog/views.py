from django.db.models import (
    Avg,
    Max,
    Min,
    OuterRef,
    Prefetch,
    Subquery,
    Sum,
    Q,
)
from rest_framework import views, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from users import models as mu

from catalog import models as m
from catalog.mixins import CategoryTreeOptimizerMixin

from . import serializers as s
from .pagination import DefaultCursorPagination, FilterValuesPagination
from .utils import get_limited_data, prefetch_tree_data


class ProductCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.ProductCatalogSerializer
    pagination_class = DefaultCursorPagination

    def get_queryset(self):
        user = self.request.user
        queryset = m.Product.objects.filter(shop__is_active=True)

        # --- ДИНАМИЧЕСКАЯ ФИЛЬТРАЦИЯ ---
        filter_map = {
            # Категории (odezhda, obuv и т.д. на фронте приходят как отдельные ключи)
            "categories": "category__slug__in",
            "odezhda": "category__slug__in",
            "obuv": "category__slug__in",
            # Бренды и Магазины
            "brands": "brand__slug__in",
            "shops": "shop__slug__in",
            # Тип продукта (в модели поле product_type)
            "product_types": "product_type__slug__in",
            # Атрибуты (Материал, Размер и т.д.)
            "material": "variants__attribute_values__id__in",
            "razmer": "variants__attribute_values__id__in",
        }

        # Проходим по всем параметрам в URL
        for param_key in self.request.query_params:
            clean_key = param_key.replace("[]", "")

            if clean_key in filter_map:
                values = self.request.query_params.getlist(param_key)
                if values:
                    lookup = filter_map[clean_key]
                    queryset = queryset.filter(**{lookup: values})

        # --- ПОИСК ПО НАЗВАНИЮ И ОПИСАНИЮ ---
        search_query = self.request.query_params.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query)
            )

        # --- ЛОГИКА ПОДЗАПРОСОВ ---
        variants_with_prices = m.ProductVariant.objects.filter(
            product=OuterRef("pk"), is_active=True
        ).with_prices(user=user)

        main_image_sq = m.ProductImage.objects.filter(
            variant__product=OuterRef("pk"), is_main=True
        ).values("image")

        from django.db.models import Case, When, IntegerField
        
        return (
            queryset.annotate(
                api_price=Subquery(
                    variants_with_prices.order_by("discounted_price").values(
                        "discounted_price"
                    )[:1]
                ),
                api_old_price=Min("variants__price"),
                api_image=Subquery(main_image_sq[:1]),
                api_rating=Avg("variants__reviews__rating"),
                api_stock=Sum("variants__stock"),
                # Явное значение для сортировки:
                # товары с наличием = 1, без наличия = 0
                has_stock=Case(
                    When(api_stock__gt=0, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
            .select_related("brand", "shop")
            .distinct()
            .order_by("-has_stock", "-api_stock")
        )


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


# export interface DefaultApiAction<T> {
#   success: boolean
#   data?: T
#   error?: { data: DefaultErrorResponse }
# }


class FiltersViewSet(viewsets.ViewSet):
    pagination_class = FilterValuesPagination

    def list(self, request, *args, **kwargs):
        has_categories = "categories" in request.query_params
        has_types = "types" in request.query_params
        has_filter_properties = "filter_properties" in request.query_params

        # Сценарий 1: Запрос всех свойств (Категории + Типы + Мета)
        if has_filter_properties:
            return Response(
                {
                    "categories": self._get_custom_categories(request),
                    "product_types": self._get_custom_types(request),
                    "meta": self.meta(request).data,
                }
            )

        # Сценарий 2: Делегирование
        if has_types and has_categories:
            return self.meta(request)

        if has_categories:
            # Если только категории, возвращаем типы (кастомно для списка)
            return Response(self._get_custom_types(request))

        # По умолчанию возвращаем категории
        return Response({"categories": self._get_custom_categories(request)})

    # --- Методы с кастомной пагинацией (используются в list) ---

    def _get_custom_categories(self, request):
        # Запрос всё еще ленивый, в базу не идет
        queryset = m.Category.objects.filter(level=0)

        # Описываем логику префетча для конкретного кусочка данных
        def prepare_categories(instances, context):
            # Передаем только 20 инстансов, а не 100500
            updated_context = prefetch_tree_data(
                instances, context, relation_path=""
            )
            return instances, updated_context

        return get_limited_data(
            request,
            queryset,
            s.CategorySerializer,
            prefix="category",
            name="Категория",
            context={"depth": 3},
            prepare_results=prepare_categories,
        )

    def _get_custom_types(self, request):
        categories = request.query_params.getlist("categories")
        qs = m.ProductType.objects.all()

        if categories and categories[0] != "/":
            # Используем distinct только если есть фильтрация, чтобы не грузить БД
            qs = qs.filter(products__category__slug__in=categories).distinct()

        return get_limited_data(
            request,
            qs,
            s.ProductTypeSerializer,
            prefix="product_tag",
            name="Тип товара",
        )

    # ------

    def meta(self, request, *args, **kwargs):
        categories = request.query_params.getlist("categories")
        types = request.query_params.getlist("types")

        # Фильтрация QuerySet продуктов
        product_qs = m.Product.objects.all()
        if categories and categories[0] != "/":
            product_qs = product_qs.filter(
                category__slug__in=categories
            ).distinct()
            if types and types[0] != "/":
                product_qs = product_qs.filter(
                    product_type__slug__in=types
                ).distinct()

        # Формируем блоки данных
        data = {
            "brands": get_limited_data(
                request,
                m.Brand.objects.filter(products__in=product_qs).distinct(),
                s.BrandSerializer,
                "brands",
                "Бренды",
            ),
            "shops": get_limited_data(
                request,
                mu.Shop.objects.filter(products__in=product_qs).distinct(),
                s.ShopSerializer,
                "shops",
                "Магазины",
            ),
            "attributes": get_limited_data(
                request,
                m.Attribute.objects.filter(products__in=product_qs)
                .distinct()
                .prefetch_related("attribute_values"),
                s.AttributesSerializer,
                "attributes",
                "Атрибуты",
                list_key="children",
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
