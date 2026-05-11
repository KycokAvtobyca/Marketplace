from django.contrib import admin

from . import models


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
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


@admin.register(models.FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = (
        "favorite",
        "product_variant",
        "date_time_create",
    )

    search_fields = (
        "favorite__user__phone_number",
        "product_variant__sku",
    )

    list_filter = ("date_time_create",)

    readonly_fields = (
        "favorite",
        "product_variant",
        "date_time_create",
    )

    list_per_page = 30
