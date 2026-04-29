from rest_framework import generics, serializers
from django.conf import settings
from .models import Category, Product, ProductTag, Brand, Attribute, 


class CategoryTreeSerializer(generics.ListAPIView):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "children"]

    def get_children(self, obj):
        children = obj.children.all()

        if children.exists():
            return CategoryTreeSerializer(children, many=True).data
        return []


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL


class AttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute


class ProductSerializer(serializers.ModelSerializer):
    category = CategoryTreeSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    tags = TagsSerializer(read_only=True)
    attributes = AttributesSerializer(read_only=True)

    class Meta:
        model = Product
        exclude = ["description", "updated_by"]
