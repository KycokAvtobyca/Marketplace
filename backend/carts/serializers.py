from catalog.models import ProductVariant
from decimal import Decimal
from rest_framework import serializers

from .models import Cart, CartItem


class ProductVariantBriefSerializer(serializers.ModelSerializer):
    """Краткая инфа о товаре для списков корзины и избранного"""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    brand = serializers.CharField(
        source="product.brand.name", allow_null=True, read_only=True
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "sku",
            "product_name",
            "product_id",
            "product_slug",
            "brand",
            "price",
            "final_price",
            "stock",
            "image",
        ]

    def get_image(self, obj):
        main_img = obj.images.filter(is_main=True).first()
        if main_img:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(main_img.image.url)
                if request
                else main_img.image.url
            )
        return None


class CartItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantBriefSerializer(read_only=True)
    total_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )

    class Meta:
        model = CartItem
        fields = ["id", "product_variant", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_items_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    total_cost = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    promocode_code = serializers.CharField(
        source="promocode.code", read_only=True, allow_null=True
    )
    promocode_discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "cart_items",
            "total_items_price",
            "total_cost",
            "promocode",
            "promocode_code",
            "promocode_discount",
        ]

    def get_promocode_discount(self, obj):
        if not obj.promocode_id:
            return "0.00"

        discount = Decimal(obj.total_items_price) - Decimal(obj.total_cost)
        return f"{max(Decimal('0.00'), discount):.2f}"
