import random

from django.conf import settings
from django.utils import timezone
from phonenumber_field.phonenumber import to_python
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import HybridTokenSerializer, ShopSerializer

from .models import Shop, SMSCode
from .throttling import (
    AuthTokenByPhone,
    AuthTokenIPThrottle,
    SMSByPhoneThrottle,
    SMSIpThrottle,
)


class HybridTokenObtainView(TokenObtainPairView):
    serializer_class = HybridTokenSerializer
    throttle_classes = [AuthTokenByPhone, AuthTokenIPThrottle]

    def post(self, request, *args, **kwargs):
        # Он внутри себя создаст экземпляр HybridTokenSerializer,
        # вызовет validate() и вернет Response с токенами в JSON.
        print(request.data)

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Достаем токены, которые приготовил нам сериализатор
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Прячем их в HttpOnly куки
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=settings.SIMPLE_JWT[
                    "ACCESS_TOKEN_LIFETIME"
                ].total_seconds(),
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=settings.SIMPLE_JWT[
                    "REFRESH_TOKEN_LIFETIME"
                ].total_seconds(),
            )

            del response.data["access"]
            del response.data["refresh"]

        return response


class SendSMSView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SMSByPhoneThrottle, SMSIpThrottle]

    def post(self, request):
        phone_raw = request.data.get("phone_number")
        phone_obj = to_python(phone_raw)
        print(request, phone_raw, phone_obj)

        if not phone_obj or not phone_obj.is_valid():
            return Response(
                {"phone_number": "Неверный формат номера телефона (РФ)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone_normalized = str(phone_obj)

        # last_code = SMSCode.objects.filter(
        #     phone_number=phone_normalized
        # ).first()

        # if last_code:
        #     time_passed = timezone.now() - last_code.date_time_create

        #     if time_passed < timezone.timedelta(seconds=60):
        #         seconds_left = 60 - int(time_passed.total_seconds())
        #         return Response(
        #             {
        #                 "error": f"Следующий код можно запросить через {seconds_left} сек."
        #             },
        #             status=status.HTTP_429_TOO_MANY_REQUESTS,
        #         )

        # last_code.delete()

        code = f"{random.randint(0, 999999):06d}"

        # Удаляем истекшие смс-кода
        expiry_time = timezone.now() - timezone.timedelta(minutes=1)
        SMSCode.objects.filter(date_time_create__lt=expiry_time).delete()

        # Создаем смс-код
        SMSCode.objects.create(phone_number=phone_normalized, code=code)

        print("\n" + "=" * 30)
        print(f"SMS ДЛЯ НОМЕРА: {phone_normalized}")
        print(f"КОД ПОДТВЕРЖДЕНИЯ: {code}")
        print("=" * 30 + "\n")

        return Response({"message": "Код успешно отправлен"})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Уже в request благодаря JWTAuthentication
        return Response(
            {
                "id": user.id,
                "phone_number": str(user.phone_number),
                # Позже добавить и другие поля
            }
        )


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
