from rest_framework import serializers

from .models import Discount, PromoCode


TARGET_FIELDS = [
    "is_global",
    "category",
    "brand",
    "tag",
    "product",
    "product_variant",
    "segment",
    "user",
]

EXCLUSION_FIELDS = [
    "excluded_categories",
    "excluded_brands",
    "excluded_tags",
    "excluded_products",
    "excluded_variants",
    "excluded_segments",
    "excluded_users",
]


class MarketingTargetSerializerMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance

        is_global = attrs.get(
            "is_global", getattr(instance, "is_global", False)
        )
        filled_targets = [
            field
            for field in TARGET_FIELDS
            if field != "is_global"
            and attrs.get(field, getattr(instance, field, None))
        ]

        if is_global and filled_targets:
            raise serializers.ValidationError(
                "Глобальная акция или промокод не может одновременно иметь целевой объект."
            )

        if not is_global and len(filled_targets) != 1:
            raise serializers.ValidationError(
                "Укажите ровно один целевой объект или включите поле is_global."
            )

        return attrs


class DiscountSerializer(MarketingTargetSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "valid_from",
            "valid_to",
            "discount_percentage",
            "can_use_with_promocode",
            "is_global",
            "category",
            "brand",
            "tag",
            "product",
            "product_variant",
            "segment",
            "user",
            *EXCLUSION_FIELDS,
        ]
        read_only_fields = ["id"]


class PromoCodeSerializer(MarketingTargetSerializerMixin, serializers.ModelSerializer):
    discount_value = serializers.SerializerMethodField()
    discount_type = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = [
            "id",
            "code",
            "description",
            "is_active",
            "valid_from",
            "valid_to",
            "usage_limit",
            "current_usage",
            "min_amount",
            "amount",
            "discount_percentage",
            "discount_type",
            "discount_value",
            "is_global",
            "category",
            "brand",
            "tag",
            "product",
            "product_variant",
            "segment",
            "user",
            *EXCLUSION_FIELDS,
        ]
        read_only_fields = ["id", "current_usage", "discount_type", "discount_value"]

    def get_discount_type(self, obj):
        if obj.amount:
            return "fixed"
        return "percent"

    def get_discount_value(self, obj):
        if obj.amount:
            return str(obj.amount)
        return str(obj.discount_percentage)

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance
        discount_percentage = attrs.get(
            "discount_percentage",
            getattr(instance, "discount_percentage", 0),
        )
        amount = attrs.get("amount", getattr(instance, "amount", None))
        has_percentage = discount_percentage and discount_percentage > 0
        has_amount = amount is not None and amount > 0

        if has_percentage and has_amount:
            raise serializers.ValidationError(
                "Промокод не может иметь процентную и фиксированную скидку одновременно."
            )

        if not has_percentage and not has_amount:
            raise serializers.ValidationError(
                "Укажите размер скидки: процент или фиксированную сумму."
            )

        return attrs
