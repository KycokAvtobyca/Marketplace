import random

from api.authentication import HttpOnlyJWTAuthentication
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from phonenumber_field.phonenumber import to_python
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import (
    HybridTokenSerializer,
    PhoneChangeSerializer,
    ShopCreateSerializer,
    ShopSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

from .models import CustomUser, Shop, SMSCode
from .throttling import (
    # AuthTokenByPhone,
    # AuthTokenIPThrottle,
    SMSByPhoneThrottle,
    SMSIpThrottle,
)


class HybridTokenObtainView(TokenObtainPairView):
    serializer_class = HybridTokenSerializer
    # throttle_classes = [AuthTokenByPhone, AuthTokenIPThrottle]

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
                secure=False,  # settings.DEBUG is False
                samesite="Lax",
                path="/",
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


@method_decorator(csrf_exempt, name="dispatch")
class HttpOnlyTokenRefreshView(TokenRefreshView):
    # Убираем все, что может потребовать CSRF
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        # Логика рефреша из кук
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get("access")
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
                max_age=settings.SIMPLE_JWT[
                    "ACCESS_TOKEN_LIFETIME"
                ].total_seconds(),
            )
            del response.data["access"]
        return response


@method_decorator(csrf_exempt, name="dispatch")
class SendSMSView(APIView):
    authentication_classes = []
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
    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneChangeView(APIView):
    """Двухэтапная смена телефона через SMS."""

    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [SMSByPhoneThrottle, SMSIpThrottle]

    def post(self, request):
        """Этап 1: Отправка SMS на текущий номер для подтверждения."""
        action = request.data.get("action")
        old_phone = str(request.user.phone_number)

        if action == "send_old":
            code = f"{random.randint(0, 999999):06d}"
            expiry_time = timezone.now() - timezone.timedelta(minutes=1)
            SMSCode.objects.filter(date_time_create__lt=expiry_time).delete()
            SMSCode.objects.create(phone_number=old_phone, code=code)

            print("\n" + "=" * 30)
            print(f"SMS СМЕНА ТЕЛЕФОНА - СТАРЫЙ НОМЕР: {old_phone}")
            print(f"КОД ПОДТВЕРЖДЕНИЯ: {code}")
            print("=" * 30 + "\n")

            return Response({"message": "Код отправлен на текущий номер"})

        elif action == "verify_old":
            code = request.data.get("code")
            valid_code = SMSCode.objects.filter(
                phone_number=old_phone,
                code=code,
                date_time_create__gte=timezone.now()
                - timezone.timedelta(minutes=1),
            ).first()

            if not valid_code:
                return Response(
                    {"code": "Неверный или просроченный код"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            valid_code.delete()
            return Response({"verified": True, "message": "Старый номер подтвержден"})

        elif action == "send_new":
            new_phone_raw = request.data.get("new_phone")
            new_phone_obj = to_python(new_phone_raw)

            if not new_phone_obj or not new_phone_obj.is_valid():
                return Response(
                    {"phone_number": "Неверный формат номера телефона (РФ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_phone = str(new_phone_obj)

            if CustomUser.objects.filter(phone_number=new_phone).exclude(
                pk=request.user.pk
            ).exists():
                return Response(
                    {"phone_number": "Этот номер уже используется"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            code = f"{random.randint(0, 999999):06d}"
            expiry_time = timezone.now() - timezone.timedelta(minutes=1)
            SMSCode.objects.filter(date_time_create__lt=expiry_time).delete()
            SMSCode.objects.create(phone_number=new_phone, code=code)

            print("\n" + "=" * 30)
            print(f"SMS СМЕНА ТЕЛЕФОНА - НОВЫЙ НОМЕР: {new_phone}")
            print(f"КОД ПОДТВЕРЖДЕНИЯ: {code}")
            print("=" * 30 + "\n")

            return Response({"message": "Код отправлен на новый номер"})

        elif action == "verify_new":
            new_phone_raw = request.data.get("new_phone")
            new_phone_obj = to_python(new_phone_raw)
            new_phone = str(new_phone_obj)
            code = request.data.get("code")

            valid_code = SMSCode.objects.filter(
                phone_number=new_phone,
                code=code,
                date_time_create__gte=timezone.now()
                - timezone.timedelta(minutes=1),
            ).first()

            if not valid_code:
                return Response(
                    {"code": "Неверный или просроченный код"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            valid_code.delete()

            with transaction.atomic():
                request.user.phone_number = new_phone
                request.user.save()

            return Response(
                {
                    "success": True,
                    "message": "Номер телефона успешно изменен",
                    "phone_number": new_phone,
                }
            )

        return Response(
            {"action": "Неизвестное действие"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CreateShopView(APIView):
    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if hasattr(user, "shop") and user.shop.exists():
            return Response(
                {"detail": "У вас уже есть магазин"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ShopCreateSerializer(data=request.data)
        if serializer.is_valid():
            shop = serializer.save(owner=user, is_active=True)
            user.is_staff = True
            user.save()

            return Response(
                {
                    "message": "Магазин успешно создан",
                    "shop": ShopSerializer(shop).data,
                    "admin_url": "/admin/",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"message": "Выход выполнен успешно"})
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response


class MyShopView(APIView):
    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response(
                {"detail": "У вас нет магазина"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ShopSerializer(shop).data)


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer


class AdminAutoLoginView(APIView):
    """Автоматически логинит пользователя в Django admin по JWT из cookie."""

    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import login
        from django.http import HttpResponseRedirect

        user = request.user
        if not user.is_staff:
            return Response(
                {"detail": "Доступ запрещен. Необходимы права персонала."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Django login требует backend
        if not hasattr(user, "backend"):
            from django.contrib.auth.backends import ModelBackend
            user.backend = "django.contrib.auth.backends.ModelBackend"

        login(request, user)
        return HttpResponseRedirect("/admin/")
