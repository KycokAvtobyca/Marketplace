from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_variant = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product_variant", "quantity", "total_price"]
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

    def get_total_price(self, obj):
        return float(obj.total_price)


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_items_price = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "cart_items",
            "total_items_price",
            "total_cost",
            "promocode",
        ]
        read_only_fields = ["id", "total_items_price", "total_cost"]

    def get_total_items_price(self, obj):
        return float(obj.total_items_price)

    def get_total_cost(self, obj):
        return float(obj.total_cost)


class AddToCartSerializer(serializers.Serializer):
    product_variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1, max_value=999)

    def validate_quantity(self, value):
        if value < 1 or value > 999:
            raise serializers.ValidationError(
                "Количество должно быть от 1 до 999"
            )
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=999)

    def validate_quantity(self, value):
        if value < 1 or value > 999:
            raise serializers.ValidationError(
                "Количество должно быть от 1 до 999"
            )
        return value
