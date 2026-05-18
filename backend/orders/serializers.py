from common.phone import PhoneValidationError, normalize_ru_mobile_phone
from catalog.models import ProductVariant
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from .models import Order, OrderItem, PickupPoint, get_default_valid_to


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
    branch_display = serializers.SerializerMethodField()

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
            "promocode",
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

    def get_branch_display(self, obj):
        if not obj.branch:
            return ""
        point = PickupPoint.objects.filter(code=obj.branch).first()
        return str(point) if point else obj.branch


class PickupPointSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = PickupPoint
        fields = ["code", "name", "address", "label"]

    def get_label(self, obj):
        return str(obj)


class OrderCreateSerializer(serializers.Serializer):
    delivery_type = serializers.ChoiceField(choices=Order.DeliveryType.choices)
    branch = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_data = serializers.JSONField(required=False, default=dict)
    name = serializers.CharField(max_length=99, min_length=2)
    phone_number = serializers.CharField()
    date_time_deliver = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=2000
    )

    def validate(self, data):
        delivery_type = data.get("delivery_type")
        branch = data.get("branch")
        address = (data.get("address") or "").strip()
        date_time_deliver = data.get("date_time_deliver")

        if delivery_type == Order.DeliveryType.PICKUP and not branch:
            raise serializers.ValidationError(
                {"branch": "Для самовывоза необходимо указать пункт выдачи."}
            )

        if delivery_type == Order.DeliveryType.PICKUP and branch:
            if not PickupPoint.objects.filter(code=branch, is_active=True).exists():
                raise serializers.ValidationError(
                    {"branch": "Выберите доступный пункт выдачи."}
                )

        if delivery_type == Order.DeliveryType.COURIER and not address:
            raise serializers.ValidationError(
                {"address": "Для доставки курьером необходимо указать адрес."}
            )

        if delivery_type == Order.DeliveryType.COURIER:
            if not date_time_deliver:
                raise serializers.ValidationError(
                    {"date_time_deliver": "Выберите время доставки."}
                )
            if date_time_deliver <= timezone.now():
                raise serializers.ValidationError(
                    {"date_time_deliver": "Время доставки должно быть в будущем."}
                )
            if len(address) < 10:
                raise serializers.ValidationError(
                    {"address": "Адрес должен быть подробнее: улица, дом и город."}
                )
            if not any(char.isdigit() for char in address):
                raise serializers.ValidationError(
                    {"address": "Укажите номер дома в адресе доставки."}
                )

        if delivery_type == Order.DeliveryType.PICKUP:
            data["address"] = None
            data["address_data"] = None
            data["date_time_deliver"] = date_time_deliver or get_default_valid_to()
        elif delivery_type == Order.DeliveryType.COURIER:
            data["branch"] = None
            data["address"] = address

        return data

    def validate_phone_number(self, value):
        try:
            return normalize_ru_mobile_phone(value)
        except PhoneValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def create(self, validated_data):
        user = self.context["request"].user
        cart = user.cart
        cart.clear_cache()

        cart_items = list(cart.cart_items.all())

        if not cart_items:
            raise serializers.ValidationError({"cart": "Корзина пуста"})

        with transaction.atomic():
            locked_variants = {
                variant.id: variant
                for variant in ProductVariant.objects.with_prices(user=user)
                .select_for_update(of=("self",))
                .select_related(
                    "product",
                    "product__brand",
                    "product__category",
                    "product__shop",
                )
                .prefetch_related("product__tags")
                .filter(id__in=[item.product_variant_id for item in cart_items])
            }

            for item in cart_items:
                variant = locked_variants[item.product_variant_id]
                item.product_variant = variant
                if variant.product.shop and variant.product.shop.owner_id == user.id:
                    raise serializers.ValidationError(
                        {
                            "cart": f"Нельзя оформить заказ на свой товар '{variant.product.name}'."
                        }
                    )
                if item.quantity > variant.stock:
                    raise serializers.ValidationError(
                        {
                            "cart": f"Недостаточно товара '{variant.product.name}'. В наличии: {variant.stock}"
                        }
                    )

            total_cost_without_sales = sum(
                item.quantity * locked_variants[item.product_variant_id].price
                for item in cart_items
            )
            if cart.promocode:
                try:
                    cart.promocode.can_use(
                        user=user,
                        order_total=cart.get_promocode_eligible_total(cart_items),
                    )
                except DjangoValidationError as exc:
                    raise serializers.ValidationError(
                        exc.message_dict
                        if hasattr(exc, "message_dict")
                        else {"promocode": exc.messages}
                    ) from exc

            total_cost = cart.calculate_total_cost(cart_items)

            order = Order.objects.create(
                user=user,
                total_cost_without_sales=total_cost_without_sales,
                total_cost=total_cost,
                promocode=cart.promocode,
                **validated_data,
            )

            for item in cart_items:
                variant = locked_variants[item.product_variant_id]
                OrderItem.objects.create(
                    order=order,
                    product_variant=variant,
                    quantity=item.quantity,
                    price_per_item=variant.price,
                    discounted_price_per_item=variant.final_price,
                )
                ProductVariant.objects.filter(pk=variant.pk).update(
                    stock=F("stock") - item.quantity
                )

            for product_id in {
                variant.product_id for variant in locked_variants.values()
            }:
                ProductVariant.sync_main_for_product(product_id)

            if cart.promocode and not cart.promocode.use():
                raise serializers.ValidationError(
                    {"promocode": "Лимит использования промокода исчерпан"}
                )

            cart.cart_items.all().delete()
            cart.promocode = None
            cart.save(update_fields=["promocode", "date_time_update"])
            cart.clear_cache()

        return order
