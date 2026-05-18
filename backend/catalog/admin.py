from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

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


class ShopReferenceAdminMixin:
    """Allow shop staff to read shared catalog dictionaries via autocomplete."""

    def _is_shop_staff(self, request):
        return (
            request.user.is_staff
            and hasattr(request.user, "shop")
            and request.user.shop.exists()
        )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or self._is_shop_staff(request)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(models.Category)
class CategoryAdmin(ShopReferenceAdminMixin, admin.ModelAdmin):
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
class BrandAdmin(ShopReferenceAdminMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.ProductTag)
class ProductTagAdmin(ShopReferenceAdminMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.ProductType)
class ProductTypeAdmin(ShopReferenceAdminMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.Attribute)
class AttributeAdmin(ShopReferenceAdminMixin, admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.AttributeValue)
class AttributeValueAdmin(ShopReferenceAdminMixin, admin.ModelAdmin):
    list_display = ("value", "attribute")
    search_fields = ("value", "attribute__name")
    list_filter = ("attribute",)

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(models.AttributeRequest)
class AttributeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shop",
        "requester",
        "attribute",
        "attribute_name",
        "value",
        "status",
        "date_time_create",
    )
    list_filter = ("status", "date_time_create")
    search_fields = (
        "attribute__name",
        "attribute_name",
        "value",
        "comment",
        "shop__name",
        "requester__phone_number",
    )
    autocomplete_fields = ("attribute",)
    readonly_fields = (
        "requester",
        "shop",
        "date_time_create",
        "date_time_update",
    )
    list_per_page = 30

    def _get_user_shop(self, request):
        if request.user.is_superuser:
            return None
        if not hasattr(request.user, "shop"):
            return None
        return request.user.shop.first()

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .select_related("requester", "shop", "attribute")
        )
        if request.user.is_superuser:
            return qs
        shop = self._get_user_shop(request)
        if shop:
            return qs.filter(shop=shop)
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            fields.extend(["status", "admin_comment"])
            if obj:
                fields.extend(
                    ["attribute", "attribute_name", "value", "comment"]
                )
        return tuple(dict.fromkeys(fields))

    def has_module_permission(self, request):
        return request.user.is_superuser or bool(self._get_user_shop(request))

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        shop = self._get_user_shop(request)
        if not shop:
            return False
        return obj is None or obj.shop_id == shop.id

    def has_add_permission(self, request):
        return request.user.is_superuser or bool(self._get_user_shop(request))

    def has_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        if not change:
            obj.requester = request.user
            if not request.user.is_superuser:
                obj.shop = self._get_user_shop(request)
        super().save_model(request, obj, form, change)


@admin.register(models.CatalogItemRequest)
class CatalogItemRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target_type",
        "name",
        "shop",
        "requester",
        "status",
        "created_object_display",
        "date_time_create",
    )
    list_filter = ("target_type", "status", "date_time_create")
    search_fields = (
        "name",
        "comment",
        "admin_comment",
        "shop__name",
        "requester__phone_number",
    )
    autocomplete_fields = ("parent_category",)
    readonly_fields = (
        "requester",
        "shop",
        "created_product_type",
        "created_category",
        "created_product_tag",
        "date_time_create",
        "date_time_update",
    )
    actions = ("approve_requests",)
    list_per_page = 30

    def _get_user_shop(self, request):
        if request.user.is_superuser:
            return None
        if not hasattr(request.user, "shop"):
            return None
        return request.user.shop.first()

    @admin.display(description="Созданный объект")
    def created_object_display(self, obj):
        return obj.created_object or "-"

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .select_related(
                "requester",
                "shop",
                "parent_category",
                "created_product_type",
                "created_category",
                "created_product_tag",
            )
        )
        if request.user.is_superuser:
            return qs
        shop = self._get_user_shop(request)
        if shop:
            return qs.filter(shop=shop)
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            fields.extend(["status", "admin_comment"])
            if obj:
                fields.extend(["target_type", "name", "parent_category", "comment"])
        return tuple(dict.fromkeys(fields))

    def has_module_permission(self, request):
        return request.user.is_superuser or bool(self._get_user_shop(request))

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        shop = self._get_user_shop(request)
        if not shop:
            return False
        return obj is None or obj.shop_id == shop.id

    def has_add_permission(self, request):
        return request.user.is_superuser or bool(self._get_user_shop(request))

    def has_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            old_status = type(obj).objects.only("status").get(pk=obj.pk).status

        if not change:
            obj.requester = request.user
            if not request.user.is_superuser:
                obj.shop = self._get_user_shop(request)

        super().save_model(request, obj, form, change)

        if (
            request.user.is_superuser
            and obj.status == models.CatalogItemRequest.Status.APPROVED
            and old_status != obj.status
        ):
            try:
                obj.approve()
            except ValidationError as exc:
                raise exc

    @admin.action(description="Утвердить выбранные заявки")
    def approve_requests(self, request, queryset):
        approved = 0
        for obj in queryset:
            try:
                obj.approve()
                approved += 1
            except ValidationError as exc:
                self.message_user(
                    request,
                    f"Заявка #{obj.pk}: {exc}",
                    level=messages.ERROR,
                )
        if approved:
            self.message_user(request, f"Утверждено заявок: {approved}")


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
    search_fields = ("name", "variants__sku")
    list_filter = ("category", "brand", "shop")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("views", "date_time_create", "date_time_update")
    inlines = [ProductVariantInline]
    list_per_page = 20
    date_hierarchy = None
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

    def changelist_view(self, request, extra_context=None):
        date_params = {
            "date_time_create__day",
            "date_time_create__month",
            "date_time_create__year",
        }
        if date_params.intersection(request.GET):
            query = request.GET.copy()
            for param in date_params:
                query.pop(param, None)
            redirect_url = request.path
            if query:
                redirect_url = f"{redirect_url}?{query.urlencode()}"
            return HttpResponseRedirect(redirect_url)
        return super().changelist_view(request, extra_context=extra_context)

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
