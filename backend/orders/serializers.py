from decimal import Decimal

from catalog.models import ProductVariant
from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_variant_name = serializers.CharField(
        source="product_variant.product.name", read_only=True
    )
    product_variant_sku = serializers.CharField(
        source="product_variant.sku", read_only=True
    )
    product_variant_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_variant",
            "product_variant_name",
            "product_variant_sku",
            "product_variant_image",
            "quantity",
            "price_per_item",
            "discounted_price_per_item",
            "total_price",
        ]

    def get_product_variant_image(self, obj):
        main_img = obj.product_variant.images.filter(is_main=True).first()
        if main_img:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(main_img.image.url)
                if request
                else main_img.image.url
            )
        return None


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    delivery_type_display = serializers.CharField(
        source="get_delivery_type_display", read_only=True
    )
    branch_display = serializers.CharField(
        source="get_branch_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "delivery_type",
            "delivery_type_display",
            "branch",
            "branch_display",
            "address",
            "address_data",
            "name",
            "phone_number",
            "description",
            "date_time_deliver",
            "total_cost_without_sales",
            "total_cost",
            "order_items",
            "date_time_create",
        ]
        read_only_fields = [
            "id",
            "status",
            "total_cost_without_sales",
            "total_cost",
            "date_time_create",
        ]


class OrderCreateSerializer(serializers.Serializer):
    delivery_type = serializers.ChoiceField(choices=Order.DeliveryType.choices)
    branch = serializers.ChoiceField(
        choices=Order.PickUpBranches.choices, required=False, allow_blank=True, allow_null=True
    )
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_data = serializers.JSONField(required=False, default=dict)
    name = serializers.CharField(max_length=99, min_length=2)
    phone_number = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=2000
    )

    def validate(self, data):
        delivery_type = data.get("delivery_type")
        branch = data.get("branch")
        address = data.get("address")

        if delivery_type == Order.DeliveryType.PICKUP and not branch:
            raise serializers.ValidationError(
                {"branch": "Для самовывоза необходимо указать пункт выдачи."}
            )

        if delivery_type == Order.DeliveryType.COURIER and not address:
            raise serializers.ValidationError(
                {"address": "Для доставки курьером необходимо указать адрес."}
            )

        # Для PICKUP: очищаем address в NULL, branch сохраняем
        if delivery_type == Order.DeliveryType.PICKUP:
            data["address"] = None
            data["address_data"] = None
        # Для COURIER: очищаем branch в NULL, address сохраняем
        elif delivery_type == Order.DeliveryType.COURIER:
            data["branch"] = None

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        cart = user.cart

        cart_items = cart.cart_items.select_related("product_variant").all()

        if not cart_items:
            raise serializers.ValidationError(
                {"cart": "Корзина пуста"}
            )

        # Проверяем остатки
        for item in cart_items:
            if item.quantity > item.product_variant.stock:
                raise serializers.ValidationError(
                    {
                        "cart": f"Недостаточно товара '{item.product_variant.product.name}'. В наличии: {item.product_variant.stock}"
                    }
                )

        with transaction.atomic():
            total_cost_without_sales = sum(
                item.quantity * item.product_variant.price for item in cart_items
            )
            total_cost = sum(
                item.quantity * item.product_variant.final_price for item in cart_items
            )

            order = Order.objects.create(
                user=user,
                total_cost_without_sales=total_cost_without_sales,
                total_cost=total_cost,
                **validated_data,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_variant=item.product_variant,
                    quantity=item.quantity,
                    price_per_item=item.product_variant.price,
                    discounted_price_per_item=item.product_variant.final_price,
                )

                # Уменьшаем остаток
                item.product_variant.stock -= item.quantity
                item.product_variant.save()

            # Очищаем корзину
            cart.cart_items.all().delete()
            cart.clear_cache()

        return order
