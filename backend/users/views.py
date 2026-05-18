import random

from common.phone import PhoneValidationError, normalize_ru_mobile_phone
from api.authentication import HttpOnlyJWTAuthentication
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import (
    HybridTokenSerializer,
    PhoneChangeSerializer,
    ShopCreateSerializer,
    ShopModerationRequestSerializer,
    ShopSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

from .models import CustomUser, Shop, ShopModerationRequest, SMSCode
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

        if response.status_code == 200 and response.data.get("access"):
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
        try:
            phone_normalized = normalize_ru_mobile_phone(phone_raw)
        except PhoneValidationError as exc:
            return Response(
                {"phone_number": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        # Создаем или обновляем смс-код
        SMSCode.objects.update_or_create(
            phone_number=phone_normalized,
            defaults={"code": code, "date_time_create": timezone.now()},
        )

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
            SMSCode.objects.update_or_create(
                phone_number=old_phone,
                defaults={"code": code, "date_time_create": timezone.now()},
            )

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
            try:
                new_phone = normalize_ru_mobile_phone(new_phone_raw)
            except PhoneValidationError as exc:
                return Response(
                    {"phone_number": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
            SMSCode.objects.update_or_create(
                phone_number=new_phone,
                defaults={"code": code, "date_time_create": timezone.now()},
            )

            print("\n" + "=" * 30)
            print(f"SMS СМЕНА ТЕЛЕФОНА - НОВЫЙ НОМЕР: {new_phone}")
            print(f"КОД ПОДТВЕРЖДЕНИЯ: {code}")
            print("=" * 30 + "\n")

            return Response({"message": "Код отправлен на новый номер"})

        elif action == "verify_new":
            new_phone_raw = request.data.get("new_phone")
            try:
                new_phone = normalize_ru_mobile_phone(new_phone_raw)
            except PhoneValidationError as exc:
                return Response(
                    {"phone_number": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
        if ShopModerationRequest.objects.filter(
            user=user,
            action=ShopModerationRequest.Action.CREATE,
            status=ShopModerationRequest.Status.NEW,
        ).exists():
            return Response(
                {"detail": "Заявка на создание магазина уже находится на модерации."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ShopCreateSerializer(data=request.data)
        if serializer.is_valid():
            request_obj = ShopModerationRequest.objects.create(
                user=user,
                action=ShopModerationRequest.Action.CREATE,
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
                image=serializer.validated_data.get("image"),
            )

            return Response(
                {
                    "message": "Заявка на создание магазина отправлена на модерацию.",
                    "request": ShopModerationRequestSerializer(request_obj).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteShopRequestView(APIView):
    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response(
                {"detail": "У вас нет магазина."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if ShopModerationRequest.objects.filter(
            user=request.user,
            shop=shop,
            action=ShopModerationRequest.Action.DELETE,
            status=ShopModerationRequest.Status.NEW,
        ).exists():
            return Response(
                {"detail": "Заявка на удаление магазина уже находится на модерации."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request_obj = ShopModerationRequest.objects.create(
            user=request.user,
            shop=shop,
            action=ShopModerationRequest.Action.DELETE,
            name=shop.name,
            description=shop.description,
        )
        return Response(
            {
                "message": "Заявка на удаление магазина отправлена на модерацию.",
                "request": ShopModerationRequestSerializer(request_obj).data,
            },
            status=status.HTTP_201_CREATED,
        )


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


class ShopReportOptionsView(APIView):
    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from catalog.models import Brand, Category, Product, ProductType

        if not request.user.is_staff:
            return Response(
                {"detail": "Доступ запрещен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        shop = (
            Shop.objects.filter(pk=request.query_params.get("shop")).first()
            if request.user.is_superuser and request.query_params.get("shop")
            else Shop.objects.filter(owner=request.user).first()
        )

        if not shop and request.user.is_superuser:
            shop = Shop.objects.order_by("name").first()

        if not shop:
            return Response(
                {"detail": "У пользователя нет магазина для отчета."},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = Product.objects.filter(shop=shop)

        categories = Category.objects.filter(product__in=products).distinct()
        product_types = ProductType.objects.filter(products__in=products).distinct()
        brands = Brand.objects.filter(products__in=products).distinct()

        serialize = lambda qs: [
            {"id": obj.pk, "name": obj.name} for obj in qs.order_by("name")
        ]

        return Response(
            {
                "categories": serialize(categories),
                "product_types": serialize(product_types),
                "brands": serialize(brands),
            }
        )


from rest_framework.permissions import BasePermission


class IsSuperuserOrReadOnly(BasePermission):
    """
    Разрешает суперпользователю полный доступ.
    Остальным - только чтение.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_superuser


class ShopViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    
    def get_queryset(self):
        """
        Суперпользователь видит все магазины.
        Остальные видят только активные магазины.
        """
        if self.request.user and self.request.user.is_superuser:
            return Shop.objects.all()
        return Shop.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        """
        При создании магазина суперпользователем:
        - Если owner не указан, устанавливается текущий пользователь
        - Магазин активируется
        """
        owner = serializer.validated_data.get('owner')
        if not owner:
            owner = self.request.user
        
        shop = serializer.save(owner=owner, is_active=True)
        
        # Если owner не суперпользователь, делаем его staff
        if not owner.is_staff:
            owner.is_staff = True
            owner.save()
    
    def perform_update(self, serializer):
        """
        При обновлении магазина суперпользователем.
        """
        shop = serializer.save()
        
        # Если owner не суперпользователь, делаем его staff
        if shop.owner and not shop.owner.is_staff:
            shop.owner.is_staff = True
            shop.owner.save()


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
