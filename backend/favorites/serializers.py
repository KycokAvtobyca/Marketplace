from rest_framework import serializers

from .models import Favorite, FavoriteItem


class FavoriteItemSerializer(serializers.ModelSerializer):
    product_variant = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteItem
        fields = ["id", "product_variant"]
        read_only_fields = ["id"]

    def get_product_variant(self, obj):
        variant = obj.product_variant
        return {
            "id": variant.id,
            "sku": variant.sku,
            "product_name": variant.product.name,
            "product_slug": variant.product.slug,
            "brand": variant.product.brand.name
            if variant.product.brand
            else None,
            "price": float(variant.price),
            "final_price": float(variant.final_price),
            "stock": variant.stock,
            "image": variant.get_main_image_url(),
        }


class FavoriteSerializer(serializers.ModelSerializer):
    favorite_items = FavoriteItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ["id", "favorite_items", "items_count"]
        read_only_fields = ["id"]

    def get_items_count(self, obj):
        return obj.favorite_items.count()


class AddToFavoriteSerializer(serializers.Serializer):
    product_variant_id = serializers.IntegerField()
