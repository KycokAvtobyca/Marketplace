from django.contrib import admin

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
