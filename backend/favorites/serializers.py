from carts.serializers import (
    ProductVariantBriefSerializer,  # Импортируем из корзины
)
from rest_framework import serializers

from .models import Favorite, FavoriteItem


class FavoriteItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantBriefSerializer(read_only=True)

    class Meta:
        model = FavoriteItem
        fields = ["id", "product_variant"]


class FavoriteSerializer(serializers.ModelSerializer):
    favorite_items = FavoriteItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "favorite_items", "items_count"]
