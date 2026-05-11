from django.contrib import admin

from . import models


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    fields = (
        "product_variant",
        "quantity",
        "price_per_item",
    )
    readonly_fields = (
        "product_variant",
        "price_per_item",
    )
    can_delete = False


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
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
    )

    inlines = [OrderItemInline]
    list_per_page = 20
    date_hierarchy = "date_time_create"

    def has_delete_permission(self, request, obj=None):
        return False


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
    )

    list_per_page = 30

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
