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

        # if "username" in self.fields:
        #     del self.fields["username"]
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


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        exclude = ["id"]
