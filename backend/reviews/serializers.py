from catalog.models import AttributeValue
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import (
    ProductComplaint,
    ProductQuestion,
    Review,
    ReviewComplaint,
    ReviewImage,
)


class ReviewImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ReviewImage
        fields = ["id", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class AttributeValueSimpleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="value")
    attribute = serializers.CharField(source="attribute.name", read_only=True)

    class Meta:
        model = AttributeValue
        fields = ["id", "name", "attribute"]


class ReviewVariantInfoSerializer(serializers.Serializer):
    """Информация о варианте товара для отзыва"""

    sku = serializers.CharField()
    attribute_values = serializers.SerializerMethodField()

    def get_attribute_values(self, obj):
        if hasattr(obj, "attribute_values"):
            return AttributeValueSimpleSerializer(
                obj.attribute_values.all(), many=True
            ).data
        return []


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(
        source="review_images", many=True, read_only=True
    )
    author_name = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    current_user_vote = serializers.SerializerMethodField()
    variant_info = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "product_variant",
            "rating",
            "description",
            "status",
            "is_verified_purchase",
            "useful_count",
            "unuseful_count",
            "author_name",
            "user_id",
            "current_user_vote",
            "variant_info",
            "date_time_create",
            "date_time_update",
            "images",
        ]
        read_only_fields = [
            "id",
            "status",
            "is_verified_purchase",
            "useful_count",
            "unuseful_count",
            "author_name",
            "user_id",
            "current_user_vote",
            "variant_info",
            "date_time_create",
            "date_time_update",
            "images",
        ]

    def get_author_name(self, obj):
        if not obj.user:
            return "Пользователь"
        return obj.user.name or "Пользователь"

    def get_current_user_vote(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None
        existing_vote = obj.votes.filter(user=request.user).first()
        return existing_vote.value if existing_vote else None

    def get_variant_info(self, obj):
        if obj.product_variant:
            serializer = ReviewVariantInfoSerializer(obj.product_variant)
            return serializer.data
        return None

    def validate(self, attrs):
        if self.instance and "product_variant" in attrs:
            if attrs["product_variant"].pk != self.instance.product_variant_id:
                raise serializers.ValidationError(
                    {
                        "product_variant": "Нельзя перенести отзыв на другой товар."
                    }
                )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        review = Review(user=request.user, **validated_data)
        try:
            review.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc
        review.save()
        return review


class ProductQuestionSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    answered_by_name = serializers.SerializerMethodField()
    question_status_display = serializers.CharField(
        source="get_question_status_display", read_only=True
    )
    answer_status_display = serializers.CharField(
        source="get_answer_status_display", read_only=True
    )
    moderation_status = serializers.SerializerMethodField()
    answer_moderation_status = serializers.SerializerMethodField()

    class Meta:
        model = ProductQuestion
        fields = [
            "id",
            "product",
            "product_name",
            "text",
            "answer",
            "author_name",
            "user_id",
            "answered_by_name",
            "answered_at",
            "is_public",
            "question_status",
            "question_status_display",
            "answer_status",
            "answer_status_display",
            "moderation_status",
            "answer_moderation_status",
            "date_time_create",
            "date_time_update",
        ]
        read_only_fields = [
            "id",
            "answer",
            "author_name",
            "user_id",
            "product_name",
            "answered_by_name",
            "answered_at",
            "is_public",
            "question_status",
            "question_status_display",
            "answer_status",
            "answer_status_display",
            "moderation_status",
            "answer_moderation_status",
            "date_time_create",
            "date_time_update",
        ]

    def get_author_name(self, obj):
        if not obj.user:
            return "Пользователь"
        return obj.user.name or "Пользователь"

    def get_answered_by_name(self, obj):
        if not obj.answered_by:
            return ""
        shop = obj.product.shop
        return shop.name if shop else obj.answered_by.name or "Продавец"

    def get_answer(self, obj):
        if obj.answer_status == ProductQuestion.AnswerStatus.APPROVED:
            return obj.answer
        return ""

    def get_moderation_status(self, obj):
        return {
            "status": obj.question_status,
            "label": obj.get_question_status_display(),
        }

    def get_answer_moderation_status(self, obj):
        if obj.answer_status == ProductQuestion.AnswerStatus.NONE:
            return None
        return {
            "status": obj.answer_status,
            "label": obj.get_answer_status_display(),
        }

    def create(self, validated_data):
        request = self.context["request"]
        return ProductQuestion.objects.create(user=request.user, **validated_data)


class ReviewComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComplaint
        fields = [
            "id",
            "review",
            "reason",
            "text",
            "status",
            "date_time_create",
            "date_time_update",
        ]
        read_only_fields = [
            "id",
            "status",
            "date_time_create",
            "date_time_update",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        review = attrs.get("review")
        if ReviewComplaint.objects.filter(
            user=request.user,
            review=review,
        ).exists():
            raise serializers.ValidationError(
                {"review": "Вы уже отправили жалобу на этот отзыв."}
            )
        return attrs

    def create(self, validated_data):
        return ReviewComplaint.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )


class ProductComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComplaint
        fields = [
            "id",
            "product",
            "reason",
            "text",
            "status",
            "date_time_create",
            "date_time_update",
        ]
        read_only_fields = [
            "id",
            "status",
            "date_time_create",
            "date_time_update",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        product = attrs.get("product")
        if ProductComplaint.objects.filter(
            user=request.user,
            product=product,
        ).exists():
            raise serializers.ValidationError(
                {"product": "Вы уже отправили жалобу на этот товар."}
            )
        return attrs

    def create(self, validated_data):
        return ProductComplaint.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
