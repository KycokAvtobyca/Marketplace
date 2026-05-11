from django.contrib import admin

from . import models


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product_variant", "rating", "status")
    search_fields = ("user__name", "product_variant__sku")
    list_filter = ("status", "rating")
    readonly_fields = (
        "user",
        "product_variant",
        "date_time_create",
        "date_time_update",
    )
    list_per_page = 20


@admin.register(models.ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "image")
    search_fields = ("review__id", "review__user__name")
    readonly_fields = ("review",)
