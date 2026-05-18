from decimal import Decimal, InvalidOperation

from django.db.models import (
    Avg,
    Count,
    F,
    Max,
    Min,
    OuterRef,
    Prefetch,
    Exists,
    Q,
    Subquery,
    Sum,
)
from rest_framework import permissions, serializers, views, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from users import models as mu

from catalog import models as m
from catalog.mixins import CategoryTreeOptimizerMixin

from . import serializers as s
from .pagination import (
    DefaultCursorPagination,
    FilterValuesPagination,
    ProductCatalogPagination,
)
from .utils import get_limited_data, prefetch_tree_data


class ProductCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.ProductCatalogSerializer
    pagination_class = ProductCatalogPagination

    @staticmethod
    def query_values(query_params, *keys):
        values = []
        for key in keys:
            values.extend(query_params.getlist(key))
            values.extend(query_params.getlist(f"{key}[]"))
        return [value for value in values if value and value != "/"]

    @staticmethod
    def category_ids_for_slugs(slugs):
        clean_slugs = [slug for slug in slugs if slug and slug != "/"]
        if not clean_slugs:
            return []

        ids = set()
        categories = m.Category.objects.filter(slug__in=clean_slugs)
        for category in categories:
            ids.update(
                category.get_descendants(include_self=True).values_list(
                    "id", flat=True
                )
            )
        return list(ids)

    @staticmethod
    def attribute_value_groups(query_params):
        explicit_keys = {"attributes", "attribute_values", "values"}
        attribute_slugs = set(
            m.Attribute.objects.filter(is_active=True).values_list("slug", flat=True)
        )
        value_ids = set()

        for param_key in query_params:
            clean_key = param_key.replace("[]", "")
            is_attribute_key = (
                clean_key in explicit_keys
                or clean_key.startswith("value_")
                or clean_key in attribute_slugs
            )
            if not is_attribute_key:
                continue

            for raw_value in query_params.getlist(param_key):
                try:
                    value_ids.add(int(raw_value))
                except (TypeError, ValueError):
                    continue

        groups = {}
        rows = m.AttributeValue.objects.filter(pk__in=value_ids).values(
            "id",
            "attribute_id",
        )
        for row in rows:
            groups.setdefault(row["attribute_id"], []).append(row["id"])

        return groups

    @staticmethod
    def apply_attribute_groups_to_variants(queryset, attribute_groups, prefix=""):
        for value_ids in attribute_groups.values():
            queryset = queryset.filter(
                **{f"{prefix}attribute_values__id__in": value_ids}
            )
        return queryset

    def get_queryset(self):
        user = self.request.user
        visibility_filter = Q(shop__is_active=True)
        if user.is_authenticated:
            visibility_filter |= Q(shop__owner=user)
        queryset = m.Product.objects.filter(visibility_filter)

        query_params = self.request.query_params
        category_values = self.query_values(query_params, "categories", "category")

        category_ids = self.category_ids_for_slugs(category_values)
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)

        simple_filter_map = {
            "brands": "brand__slug__in",
            "shops": "shop__slug__in",
            "product_types": "product_type__slug__in",
            "types": "product_type__slug__in",
        }
        for param_key, lookup in simple_filter_map.items():
            values = self.query_values(query_params, param_key)
            if values:
                queryset = queryset.filter(**{lookup: values})

        min_price = query_params.get("price_min") or query_params.get("min_price")
        max_price = query_params.get("price_max") or query_params.get("max_price")
        min_price_decimal = None
        max_price_decimal = None
        if min_price:
            try:
                min_price_decimal = Decimal(min_price)
            except (InvalidOperation, ValueError):
                pass

        if max_price:
            try:
                max_price_decimal = Decimal(max_price)
            except (InvalidOperation, ValueError):
                pass

        attribute_groups = self.attribute_value_groups(query_params)
        matching_variants = m.ProductVariant.objects.with_prices(user=user).filter(
            product=OuterRef("pk"),
            is_active=True,
            stock__gt=0,
        )
        matching_variants = self.apply_attribute_groups_to_variants(
            matching_variants,
            attribute_groups,
        )
        if min_price_decimal is not None:
            matching_variants = matching_variants.filter(
                discounted_price__gte=min_price_decimal
            )
        if max_price_decimal is not None:
            matching_variants = matching_variants.filter(
                discounted_price__lte=max_price_decimal
            )

        if attribute_groups or min_price_decimal is not None or max_price_decimal is not None:
            queryset = queryset.filter(Exists(matching_variants))

        # --- ПОИСК ПО НАЗВАНИЮ И ОПИСАНИЮ ---
        search_query = query_params.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(brand__name__icontains=search_query)
                | Q(variants__attribute_values__value__icontains=search_query)
            )

        # --- ЛОГИКА ПОДЗАПРОСОВ ---
        variants_with_prices = m.ProductVariant.objects.filter(
            product=OuterRef("pk"), is_active=True, stock__gt=0
        ).with_prices(user=user)
        variants_with_prices = self.apply_attribute_groups_to_variants(
            variants_with_prices,
            attribute_groups,
        )

        main_image_sq = m.ProductImage.objects.filter(
            variant__product=OuterRef("pk"),
            variant__is_active=True,
            variant__stock__gt=0,
        )
        main_image_sq = self.apply_attribute_groups_to_variants(
            main_image_sq,
            attribute_groups,
            prefix="variant__",
        ).order_by("-variant__is_main", "-variant__stock", "-is_main", "variant_id", "pk").values("image")

        sku_sq = (
            m.ProductVariant.objects.filter(
                product=OuterRef("pk"), is_active=True, stock__gt=0
            )
        )
        sku_sq = self.apply_attribute_groups_to_variants(
            sku_sq,
            attribute_groups,
        ).order_by("-is_main", "-stock", "pk").values("sku")[:1]
        variant_id_sq = (
            m.ProductVariant.objects.filter(
                product=OuterRef("pk"), is_active=True, stock__gt=0
            )
        )
        variant_id_sq = self.apply_attribute_groups_to_variants(
            variant_id_sq,
            attribute_groups,
        ).order_by("-is_main", "-stock", "pk").values("id")[:1]

        from django.db.models import Case, IntegerField, When

        queryset = (
            queryset.annotate(
                api_price=Subquery(
                    variants_with_prices.order_by("-is_main", "-stock", "pk").values(
                        "discounted_price"
                    )[:1]
                ),
                api_old_price=Subquery(
                    variants_with_prices.order_by("-is_main", "-stock", "pk").values(
                        "price"
                    )[:1]
                ),
                api_image=Subquery(main_image_sq[:1]),
                api_sku=Subquery(sku_sq),
                api_variant_id=Subquery(variant_id_sq),
                api_rating=Avg(
                    "variants__reviews__rating",
                    filter=Q(variants__reviews__status="APPROVED"),
                ),
                api_stock=Sum(
                    "variants__stock",
                    filter=Q(variants__is_active=True, variants__stock__gt=0),
                ),
                # Явное значение для сортировки:
                # товары с наличием = 1, без наличия = 0
                has_stock=Case(
                    When(api_stock__gt=0, then=1),
                    default=0,
                    output_field=IntegerField(),
                ),
            )
            .select_related("brand", "shop")
            .distinct()
        )
        queryset = queryset.filter(api_variant_id__isnull=False)

        sort = self.request.query_params.get("sort", "new")
        sort_map = {
            "price_asc": ("-has_stock", "api_price", "id"),
            "price_desc": ("-has_stock", "-api_price", "-id"),
            "new": ("-has_stock", "-date_time_create", "-id"),
            "popular": (
                "-has_stock",
                F("api_rating").desc(nulls_last=True),
                "-views",
                "-id",
            ),
            "views_desc": ("-has_stock", "-views", "-id"),
            "rating_desc": (
                "-has_stock",
                F("api_rating").desc(nulls_last=True),
                "-id",
            ),
        }
        return queryset.order_by(*sort_map.get(sort, sort_map["new"]))


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
                    ).prefetch_related("attribute_values__attribute"),
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
        )
        visibility_filter = Q(shop__is_active=True)
        if self.request.user.is_authenticated:
            visibility_filter |= Q(shop__owner=self.request.user)
        qs = qs.filter(visibility_filter)

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

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        m.Product.objects.filter(pk=self.kwargs.get(self.lookup_field)).update(
            views=F("views") + 1
        )
        return response


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


class CatalogItemRequestViewSet(viewsets.ModelViewSet):
    serializer_class = s.CatalogItemRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]
    pagination_class = DefaultCursorPagination

    def get_queryset(self):
        qs = m.CatalogItemRequest.objects.select_related(
            "requester",
            "shop",
            "parent_category",
            "created_product_type",
            "created_category",
            "created_product_tag",
        ).order_by("-date_time_create", "-id")

        user = self.request.user
        if user.is_superuser:
            return qs

        shop = mu.Shop.objects.filter(owner=user).first()
        if not shop:
            return qs.none()

        return qs.filter(Q(requester=user) | Q(shop=shop)).distinct()

    def perform_create(self, serializer):
        shop = mu.Shop.objects.filter(owner=self.request.user).first()
        if not shop:
            raise serializers.ValidationError(
                {"shop": "Заявки на справочники может отправлять только магазин."}
            )

        serializer.save(requester=self.request.user, shop=shop)


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.ProductVariantSerializer
    pagination_class = DefaultCursorPagination

    def get_queryset(self):
        user = self.request.user

        return (
            m.ProductVariant.objects.with_prices(user=user)
            .prefetch_related("attribute_values__attribute")
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
        queryset = (
            m.Category.objects.filter(level=0)
            .annotate(children_count=Count("children"))
            .order_by("-children_count", "tree_id", "lft", "name")
        )

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
            category_ids = ProductCatalogViewSet.category_ids_for_slugs(
                categories
            )
            qs = qs.filter(products__category_id__in=category_ids).distinct()

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
            category_ids = ProductCatalogViewSet.category_ids_for_slugs(
                categories
            )
            product_qs = product_qs.filter(
                category_id__in=category_ids
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
