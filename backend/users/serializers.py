from common.phone import PhoneValidationError, normalize_ru_mobile_phone
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, PhoneBan, Shop, ShopModerationRequest, SMSCode


class HybridTokenSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField()
    sms_code = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].required = False

    def validate(self, attrs):
        try:
            phone = normalize_ru_mobile_phone(attrs.get("phone_number"))
        except PhoneValidationError as exc:
            raise serializers.ValidationError({"phone_number": str(exc)}) from exc
        if PhoneBan.is_phone_banned(phone):
            raise serializers.ValidationError(
                {
                    "detail": {
                        "message": "Ваш номер телефона заблокирован.",
                        "code": "user_blocked",
                    }
                }
            )
        password = attrs.get("password")
        code = attrs.get("sms_code")

        print(f"DEBUG: Phone: {phone}, Code: {code}")

        valid_code = SMSCode.objects.filter(
            phone_number=phone,
            code=code,
            date_time_create__gte=timezone.now()
            - timezone.timedelta(minutes=1),
        ).first()

        if not valid_code:
            raise serializers.ValidationError(
                {"code": "Неверный или просроченный код"}
            )

        user, created = CustomUser.objects.get_or_create(phone_number=phone)

        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "detail": {
                        "message": "Ваш аккаунт заблокирован.",
                        "code": "user_blocked",
                    }
                }
            )

        if user.is_superuser:
            if not password:
                return {
                    "requires_password": True,
                    "is_superuser": True,
                    "phone_number": phone,
                }

            if not user.check_password(password):
                raise serializers.ValidationError(
                    "Неверный пароль администратора"
                )

        refresh = self.get_token(user)

        valid_code.delete()

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_new_user": created,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "phone_number",
            "name",
            "last_name",
            "middle_name",
            "email",
            "address",
            "address_data",
            "is_active",
            "is_staff",
            "date_time_create",
            "date_time_update",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "name",
            "last_name",
            "middle_name",
            "email",
            "address",
            "address_data",
        )

    def validate_email(self, value):
        if not value:
            return value
        value = value.strip().lower()
        try:
            validate_email(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                "Введите корректный email, например name@example.com."
            ) from exc

        domain = value.rsplit("@", 1)[-1]
        if "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise serializers.ValidationError(
                "Введите корректный email с доменом, например name@example.com."
            )
        return value


class PhoneChangeSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=[
            "send_old",
            "verify_old",
            "send_new",
            "verify_new",
        ]
    )
    new_phone = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        exclude = ["id"]


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["name", "description", "image"]


class ShopModerationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopModerationRequest
        fields = [
            "id",
            "action",
            "status",
            "name",
            "description",
            "image",
            "admin_comment",
            "date_time_create",
        ]
        read_only_fields = ["id", "action", "status", "admin_comment", "date_time_create"]
