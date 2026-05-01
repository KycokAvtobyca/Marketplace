from rest_framework import serializers
from users.serializers import ShopSerializer

from .models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductTag,
    ProductType,
    ProductVariant,
)


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["name", "slug", "children"]

    def get_children(self, obj):
        depth = self.context.get("depth")

        if depth is None or obj.level >= int(depth):
            return []

        children = obj.get_children()
        return CategorySerializer(
            children, many=True, context=self.context
        ).data


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ["id"]


class ProductTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        exclude = ["id", "is_active"]


class AttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        exclude = ["id"]


class AttributeValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        exclude = ["attribute"]


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        exclude = ["id"]


class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_values = AttributeValuesSerializer(read_only=True, many=True)

    class Meta:
        model = ProductVariant
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    brand = BrandSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    tags = ProductTagsSerializer(read_only=True, many=True)
    attributes = AttributesSerializer(read_only=True, many=True)

    def get_category(self, obj):
        return CategorySerializer(obj.category.get_root()).data

    def get_variants(self, obj):
        variants = self.context.get("variants_flag")

        if variants is not None:
            return ProductVariantSerializer(
                obj.variants.all(), read_only=True, many=True
            ).data
        return []

    class Meta:
        model = Product
        exclude = ["description", "updated_by"]
