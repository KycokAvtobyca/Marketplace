from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from . import models


@admin.register(models.Cart)
class CartAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "user",
        "date_time_create",
    )

    search_fields = (
        "user__phone_number",
        "user__name",
    )

    list_filter = ("date_time_create",)

    readonly_fields = (
        "user",
        "date_time_create",
        "date_time_update",
    )

    list_per_page = 25


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product_variant",
        "quantity",
        "date_time_create",
    )

    search_fields = (
        "cart__user__phone_number",
        "product_variant__sku",
    )

    list_filter = ("date_time_create",)

    readonly_fields = (
        "cart",
        "product_variant",
        "date_time_create",
    )

    list_per_page = 30
