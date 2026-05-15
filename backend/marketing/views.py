from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Discount, PromoCode
from .serializers import DiscountSerializer, PromoCodeSerializer


SELLER_FORCED_EMPTY_FIELDS = {
    "is_global": False,
    "category": None,
    "brand": None,
    "tag": None,
    "segment": None,
    "user": None,
}


class StaffWriteReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class SellerScopedMarketingMixin:
    def _get_user_shop(self):
        user = self.request.user
        if not user or not user.is_authenticated or user.is_superuser:
            return None
        return user.shop.first()

    def _seller_queryset(self, qs):
        if self.request.user.is_superuser:
            return qs

        shop = self._get_user_shop()
        if shop is None:
            return qs.none()

        return (
            qs.filter(
                product__shop=shop,
                is_global=False,
                product_variant__isnull=True,
                category__isnull=True,
                brand__isnull=True,
                tag__isnull=True,
                segment__isnull=True,
                user__isnull=True,
            )
            | qs.filter(
                product_variant__product__shop=shop,
                is_global=False,
                product__isnull=True,
                category__isnull=True,
                brand__isnull=True,
                tag__isnull=True,
                segment__isnull=True,
                user__isnull=True,
            )
        ).distinct()

    def _get_target_for_seller(self, serializer):
        data = serializer.validated_data
        instance = serializer.instance

        product = data.get("product", getattr(instance, "product", None))
        variant = data.get(
            "product_variant", getattr(instance, "product_variant", None)
        )

        if bool(product) == bool(variant):
            raise ValidationError(
                "Продавец может создать промокод или акцию только для одного своего товара или варианта."
            )

        return product, variant

    def _validate_seller_scope(self, serializer):
        if self.request.user.is_superuser:
            return {}

        shop = self._get_user_shop()
        if shop is None:
            raise PermissionDenied("У пользователя нет активного магазина.")

        product, variant = self._get_target_for_seller(serializer)
        product_shop_id = getattr(product, "shop_id", None)
        variant_shop_id = getattr(getattr(variant, "product", None), "shop_id", None)

        if product_shop_id != shop.id and variant_shop_id != shop.id:
            raise PermissionDenied(
                "Продавец может создавать маркетинг только для товаров своего магазина."
            )

        excluded_products = serializer.validated_data.get("excluded_products", [])
        excluded_variants = serializer.validated_data.get("excluded_variants", [])

        if any(item.shop_id != shop.id for item in excluded_products):
            raise PermissionDenied(
                "Исключения по товарам должны относиться к вашему магазину."
            )

        if any(item.product.shop_id != shop.id for item in excluded_variants):
            raise PermissionDenied(
                "Исключения по вариантам должны относиться к вашему магазину."
            )

        return SELLER_FORCED_EMPTY_FIELDS

    def perform_create(self, serializer):
        serializer.save(**self._validate_seller_scope(serializer))

    def perform_update(self, serializer):
        serializer.save(**self._validate_seller_scope(serializer))


class DiscountViewSet(SellerScopedMarketingMixin, viewsets.ModelViewSet):
    serializer_class = DiscountSerializer
    permission_classes = [StaffWriteReadOnlyPermission]

    def get_queryset(self):
        qs = Discount.objects.all().order_by("-date_time_create", "-id")
        if self.request.method in permissions.SAFE_METHODS and not (
            self.request.user and self.request.user.is_staff
        ):
            return qs.filter(is_active=True)

        if self.request.user and self.request.user.is_staff:
            return self._seller_queryset(qs)

        return qs


class PromoCodeViewSet(SellerScopedMarketingMixin, viewsets.ModelViewSet):
    serializer_class = PromoCodeSerializer
    permission_classes = [StaffWriteReadOnlyPermission]

    def get_queryset(self):
        qs = PromoCode.objects.all().order_by("-date_time_create", "-id")
        if self.request.method in permissions.SAFE_METHODS and not (
            self.request.user and self.request.user.is_staff
        ):
            return qs.filter(is_active=True)

        if self.request.user and self.request.user.is_staff:
            return self._seller_queryset(qs)

        return qs
