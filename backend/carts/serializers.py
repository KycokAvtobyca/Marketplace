from catalog.models import ProductVariant
from common.models import SiteConfiguration
from decimal import Decimal, ROUND_HALF_UP
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
    has_promocode_discount = serializers.SerializerMethodField()
    promocode_discount = serializers.SerializerMethodField()
    promocode_final_price = serializers.SerializerMethodField()
    promocode_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_variant",
            "quantity",
            "total_price",
            "has_promocode_discount",
            "promocode_discount",
            "promocode_final_price",
            "promocode_total_price",
        ]

    def _money(self, value):
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _get_promocode_discounts(self, cart):
        if hasattr(cart, "_promocode_item_discounts"):
            return cart._promocode_item_discounts

        discounts = {}
        cart._promocode_item_discounts = discounts

        if not cart.promocode_id:
            return discounts

        items = list(cart.cart_items.all())
        eligible_total = Decimal(cart.get_promocode_eligible_total(items))
        if eligible_total <= 0 or eligible_total < cart.promocode.min_amount:
            return discounts

        base_total = Decimal(cart.get_total_items_price(items))
        if base_total <= 0:
            return discounts

        config = SiteConfiguration.load()
        max_discount_limit = eligible_total * Decimal(
            str(config.max_discount_percentage)
        )

        if cart.promocode.amount:
            proposed_discount = cart.promocode.amount
        elif cart.promocode.discount_percentage:
            proposed_discount = eligible_total * Decimal(
                str(cart.promocode.discount_percentage)
            )
        else:
            proposed_discount = Decimal("0.00")

        total_discount = min(proposed_discount, max_discount_limit, eligible_total)
        total_discount = min(
            total_discount,
            max(Decimal("0.00"), base_total - Decimal("1.00")),
        )
        if total_discount <= 0:
            return discounts

        remaining_discount = self._money(total_discount)
        eligible_items = [
            item
            for item in items
            if cart.promocode.is_applicable_to_variant(
                item.product_variant, user=cart.user
            )
        ]

        for index, item in enumerate(eligible_items):
            if index == len(eligible_items) - 1:
                item_discount = remaining_discount
            else:
                item_discount = self._money(
                    total_discount * Decimal(item.total_price) / eligible_total
                )
                remaining_discount -= item_discount

            discounts[item.pk] = min(item_discount, self._money(item.total_price))

        return discounts

    def _get_item_promocode_discount(self, obj):
        return self._get_promocode_discounts(obj.cart).get(obj.pk, Decimal("0.00"))

    def get_has_promocode_discount(self, obj):
        return self._get_item_promocode_discount(obj) > 0

    def get_promocode_discount(self, obj):
        return f"{self._get_item_promocode_discount(obj):.2f}"

    def get_promocode_total_price(self, obj):
        total = self._money(obj.total_price) - self._get_item_promocode_discount(obj)
        return f"{max(Decimal('0.00'), total):.2f}"

    def get_promocode_final_price(self, obj):
        if not obj.quantity:
            return f"{self._money(obj.product_variant.final_price):.2f}"
        total = Decimal(self.get_promocode_total_price(obj))
        return f"{self._money(total / Decimal(obj.quantity)):.2f}"


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
