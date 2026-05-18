from django.contrib import admin
from django.core.exceptions import ValidationError

from . import models


@admin.register(models.PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "address", "is_active")
    search_fields = ("name", "code", "address")
    list_filter = ("is_active",)
    prepopulated_fields = {"code": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    fields = (
        "product_variant",
        "quantity",
        "price_per_item",
        "discounted_price_per_item",
    )
    readonly_fields = (
        "product_variant",
        "price_per_item",
        "discounted_price_per_item",
    )
    can_delete = False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = request.user.shop.first()
        if shop:
            return qs.filter(product_variant__product__shop=shop)
        return qs.none()


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    CLOSED_STATUSES = {
        models.Order.Status.COMPLETED,
        models.Order.Status.PAID,
        models.Order.Status.CANCELED,
    }
    list_display = (
        "id",
        "user",
        "status",
        "delivery_type",
        "total_cost",
        "date_time_create",
    )

    search_fields = (
        "id",
        "user__phone_number",
        "phone_number",
        "name",
    )

    list_filter = (
        "status",
        "delivery_type",
        "date_time_create",
    )

    readonly_fields = (
        "id",
        "date_time_create",
        "date_time_update",
        "total_cost_without_sales",
        "total_cost",
        "discount",
        "user",
        "promocode",
        "name",
        "phone_number",
        "delivery_type",
        "branch",
        "address",
        "address_data",
        "description",
        "date_time_deliver",
    )

    inlines = [OrderItemInline]
    list_per_page = 20
    date_hierarchy = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Продавец видит заказы, содержащие его товары
        shop = request.user.shop.first()
        if shop:
            return qs.filter(
                order_items__product_variant__product__shop=shop
            ).distinct()
        return qs.none()

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        if not request.user.is_staff:
            return False
        if not hasattr(request.user, "shop"):
            return False
        return request.user.shop.exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_staff:
            return False
        shop = request.user.shop.first()
        if not shop:
            return False
        if obj is None:
            return True
        return obj.order_items.filter(
            product_variant__product__shop=shop
        ).exists()

    def has_change_permission(self, request, obj=None):
        # Продавцы могут менять только статус заказа
        if request.user.is_superuser:
            return True
        if not request.user.is_staff:
            return False
        if obj is None:
            return True
        shop = request.user.shop.first()
        if not shop:
            return False
        return obj.order_items.filter(
            product_variant__product__shop=shop
        ).exists()

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        # Продавец видит только статус для изменения
        return ("status",)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        if obj and obj.status in self.CLOSED_STATUSES:
            return ("status",)
        return ()

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status" and not request.user.is_superuser:
            kwargs["choices"] = [
                choice
                for choice in db_field.choices
                if choice[0] != models.Order.Status.PAID
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if (
            change
            and not request.user.is_superuser
            and obj.pk
            and "status" in form.changed_data
        ):
            old_status = type(obj).objects.only("status").get(pk=obj.pk).status
            if old_status in self.CLOSED_STATUSES and obj.status != old_status:
                raise ValidationError(
                    "Закрытый заказ нельзя снова сделать активным для магазина."
                )
            if obj.status == models.Order.Status.PAID:
                raise ValidationError(
                    "Статус «Оплачен после получения» может установить только администратор."
                )

        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_variant",
        "quantity",
        "price_per_item",
    )

    search_fields = (
        "order__id",
        "product_variant__sku",
        "product_variant__product__name",
    )

    list_filter = (
        "order__status",
        "order__date_time_create",
    )

    readonly_fields = (
        "order",
        "product_variant",
        "price_per_item",
        "discounted_price_per_item",
        "quantity",
    )

    list_per_page = 30

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = request.user.shop.first()
        if shop:
            return qs.filter(product_variant__product__shop=shop)
        return qs.none()

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False
