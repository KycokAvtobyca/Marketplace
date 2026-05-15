from django.contrib import admin
from django.core.exceptions import PermissionDenied

from catalog import models as catalog_models

from . import models


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_percentage",
        "is_active",
        "valid_from",
        "valid_to",
    )
    search_fields = ("name",)
    list_filter = ("is_active", "date_time_create")
    readonly_fields = ("date_time_create", "date_time_update")
    list_per_page = 20


@admin.register(models.PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "is_active",
        "discount_percentage",
        "amount",
        "usage_limit",
        "current_usage",
    )
    search_fields = ("code",)
    list_filter = ("is_active", "date_time_create")
    readonly_fields = ("date_time_create", "date_time_update", "current_usage")
    list_per_page = 30

    def _get_user_shop(self, request):
        if request.user.is_superuser:
            return None
        return request.user.shop.first()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        shop = self._get_user_shop(request)
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

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return bool(self._get_user_shop(request))

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return bool(self._get_user_shop(request))

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            fields.extend(
                [
                    "is_global",
                    "category",
                    "brand",
                    "tag",
                    "segment",
                    "user",
                ]
            )
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            shop = self._get_user_shop(request)
            if shop is not None:
                if db_field.name == "product":
                    kwargs["queryset"] = catalog_models.Product.objects.filter(
                        shop=shop
                    )
                elif db_field.name == "product_variant":
                    kwargs["queryset"] = catalog_models.ProductVariant.objects.filter(
                        product__shop=shop
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            shop = self._get_user_shop(request)
            if shop is not None:
                if db_field.name == "excluded_products":
                    kwargs["queryset"] = catalog_models.Product.objects.filter(
                        shop=shop
                    )
                elif db_field.name == "excluded_variants":
                    kwargs["queryset"] = catalog_models.ProductVariant.objects.filter(
                        product__shop=shop
                    )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            shop = self._get_user_shop(request)
            if shop is None:
                raise PermissionDenied

            product_shop_id = getattr(obj.product, "shop_id", None)
            variant_shop_id = (
                getattr(obj.product_variant.product, "shop_id", None)
                if obj.product_variant_id
                else None
            )
            is_own_product = product_shop_id == shop.id
            is_own_variant = variant_shop_id == shop.id

            if not (is_own_product or is_own_variant):
                raise PermissionDenied(
                    "Продавец может создавать промокоды только для своих товаров."
                )

            obj.is_global = False
            obj.category = None
            obj.brand = None
            obj.tag = None
            obj.segment = None
            obj.user = None

        super().save_model(request, obj, form, change)
