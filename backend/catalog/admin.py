from django.contrib import admin

from . import models


class ShopOwnerAdminMixin:
    """Миксин для ограничения доступа в админке только к данным своего магазина."""

    def _get_shop_from_obj(self, obj):
        """Определяет магазин из объекта, учитывая разные модели."""
        if obj is None:
            return None
        if hasattr(obj, "shop"):
            return getattr(obj, "shop", None)
        if hasattr(obj, "product"):
            return getattr(obj.product, "shop", None)
        if hasattr(obj, "variant"):
            return getattr(obj.variant.product, "shop", None)
        return None

    def _get_user_shop(self, request):
        if not request.user.is_staff:
            return None
        if not hasattr(request.user, "shop"):
            return None
        return request.user.shop.first()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = self._get_user_shop(request)
        if shop:
            if hasattr(self.model, "shop"):
                return qs.filter(shop=shop)
            if hasattr(self.model, "product"):
                return qs.filter(product__shop=shop)
            if hasattr(self.model, "variant"):
                return qs.filter(variant__product__shop=shop)
        return qs.none()

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return bool(self._get_user_shop(request))

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        shop = self._get_user_shop(request)
        if not shop:
            return False
        if obj is None:
            return True
        obj_shop = self._get_shop_from_obj(obj)
        return obj_shop == shop

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        shop = self._get_user_shop(request)
        if not shop:
            return False
        if obj is None:
            return True
        obj_shop = self._get_shop_from_obj(obj)
        return obj_shop == shop

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        shop = self._get_user_shop(request)
        if not shop:
            return False
        if obj is None:
            return True
        obj_shop = self._get_shop_from_obj(obj)
        return obj_shop == shop

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return bool(self._get_user_shop(request))

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            shop = self._get_user_shop(request)
            if shop and hasattr(obj, "shop"):
                obj.shop = shop
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        shop = request.user.shop.first()
        if shop is not None:
            if db_field.name == "product":
                kwargs["queryset"] = models.Product.objects.filter(shop=shop)
            elif db_field.name in ("variant", "product_variant"):
                kwargs["queryset"] = models.ProductVariant.objects.filter(
                    product__shop=shop
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "level")
    search_fields = ("name",)
    list_filter = ("level",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("level", "tree_id")
    list_per_page = 30

    def has_module_permission(self, request):
        # Категории доступны только суперпользователям
        return request.user.is_superuser


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("value", "attribute")
    search_fields = ("value", "attribute__name")
    list_filter = ("attribute",)

    def has_module_permission(self, request):
        return request.user.is_superuser


class ProductImageInline(admin.StackedInline):
    model = models.ProductImage
    extra = 0
    fields = ("image", "is_main")


class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 1
    fields = ("sku", "price", "stock", "is_active", "is_main")
    readonly_fields = ("sku",)
    autocomplete_fields = ("attribute_values",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = request.user.shop.first()
        if shop:
            return qs.filter(product__shop=shop)
        return qs.none()


@admin.register(models.Product)
class ProductAdmin(ShopOwnerAdminMixin, admin.ModelAdmin):
    list_display = ("name", "category", "brand", "shop")
    search_fields = ("name", "sku")
    list_filter = ("category", "brand", "shop")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("views", "date_time_create", "date_time_update")
    inlines = [ProductVariantInline]
    list_per_page = 20
    date_hierarchy = "date_time_create"
    autocomplete_fields = (
        "category",
        "brand",
        "product_type",
        "shop",
        "tags",
        "attributes",
    )

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return self.list_filter
        # Продавец не видит фильтр по магазинам
        return ("category", "brand")

    def get_fields(self, request, obj=None):
        """Показывает поле 'shop' только для суперпользователей."""
        fields = list(super().get_fields(request, obj))
        if not request.user.is_superuser and "shop" in fields:
            return [f for f in fields if f != "shop"]
        return fields

    def get_readonly_fields(self, request, obj=None):
        """Поле shop не readonly для суперпользователей - они должны его редактировать."""
        return super().get_readonly_fields(request, obj)


@admin.register(models.ProductVariant)
class ProductVariantAdmin(ShopOwnerAdminMixin, admin.ModelAdmin):
    list_display = ("sku", "product", "price", "stock", "is_active", "is_main")
    search_fields = ("sku", "product__name")
    list_filter = ("is_active", "is_main")
    readonly_fields = ("sku",)
    list_per_page = 30
    autocomplete_fields = ("product", "attribute_values")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = request.user.shop.first()
        if shop:
            return qs.filter(product__shop=shop)
        return qs.none()

    def get_list_filter(self, request):
        """Убрать фильтр по shop для продавцов."""
        if request.user.is_superuser:
            return self.list_filter
        return ("is_active", "is_main")


@admin.register(models.ProductImage)
class ProductImageAdmin(ShopOwnerAdminMixin, admin.ModelAdmin):
    list_display = ("variant", "is_main")
    search_fields = ("variant__sku", "variant__product__name")
    list_filter = ("is_main",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = request.user.shop.first()
        if shop:
            return qs.filter(variant__product__shop=shop)
        return qs.none()

    def get_list_filter(self, request):
        """Убрать фильтр по shop для продавцов."""
        if request.user.is_superuser:
            return self.list_filter
        return ("is_main",)
