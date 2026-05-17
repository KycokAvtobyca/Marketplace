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


@admin.register(models.ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "value", "date_time_create")
    search_fields = ("review__id", "user__phone_number", "user__name")
    list_filter = ("value", "date_time_create")
    readonly_fields = ("date_time_create", "date_time_update")


@admin.register(models.ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "is_public",
        "answered_by",
        "answered_at",
    )
    search_fields = ("product__name", "user__phone_number", "text", "answer")
    list_filter = ("is_public", "answered_at", "date_time_create")
    readonly_fields = ("user", "date_time_create", "date_time_update", "answered_at")
    autocomplete_fields = ("product",)


@admin.register(models.ReviewComplaint)
class ReviewComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "reason", "status", "date_time_create")
    search_fields = ("review__id", "user__phone_number", "text")
    list_filter = ("reason", "status", "date_time_create")
    readonly_fields = ("review", "user", "reason", "text", "date_time_create", "date_time_update")


@admin.register(models.ProductComplaint)
class ProductComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "reason", "status", "date_time_create")
    search_fields = ("product__name", "user__phone_number", "text")
    list_filter = ("reason", "status", "date_time_create")
    readonly_fields = ("product", "user", "reason", "text", "date_time_create", "date_time_update")
