from django.contrib import admin

from . import models

admin.site.register(
    [
        models.Brand,
        models.Category,
        models.Attribute,
        models.AttributeValue,
        models.Product,
        models.ProductVariant,
        models.ProductImage,
        models.ProductType,
        models.ProductTag,
    ]
)
