from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, Shop, SMSCode


class HybridTokenSerializer(TokenObtainPairSerializer):
    phone_number = PhoneNumberField(region="RU")
    sms_code = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].required = False

    def validate(self, attrs):
        phone = attrs.get("phone_number")
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

        if user.is_superuser:
            if not password:
                raise serializers.ValidationError(
                    {"password": "Пароль обязателен для администратора"}
                )

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
