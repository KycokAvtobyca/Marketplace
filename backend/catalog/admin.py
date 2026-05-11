from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "level")
    search_fields = ("name",)
    list_filter = ("level",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("level", "tree_id")
    list_per_page = 30


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20


@admin.register(models.ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("value", "attribute")
    search_fields = ("value", "attribute__name")
    list_filter = ("attribute",)


class ProductImageInline(admin.StackedInline):
    model = models.ProductImage
    extra = 0
    fields = ("image", "is_main")


class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 1
    fields = ("sku", "price", "stock", "is_active", "is_main")
    readonly_fields = ("sku",)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "shop")
    search_fields = ("name", "sku")
    list_filter = ("category", "brand", "shop")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("views", "date_time_create", "date_time_update", "slug")
    inlines = [ProductVariantInline]
    list_per_page = 20
    date_hierarchy = "date_time_create"


@admin.register(models.ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "price", "stock", "is_active", "is_main")
    search_fields = ("sku", "product__name")
    list_filter = ("is_active", "is_main", "product__category")
    readonly_fields = ("sku",)
    list_per_page = 30


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("variant", "is_main")
    search_fields = ("variant__sku", "variant__product__name")
    list_filter = ("is_main",)
