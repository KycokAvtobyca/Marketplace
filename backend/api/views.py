from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import HybridTokenSerializer


class HybridTokenObtainView(TokenObtainPairView):
    serializer_class = HybridTokenSerializer

    def post(self, request, *args, **kwargs):
        # Он внутри себя создаст экземпляр HybridTokenSerializer,
        # вызовет validate() и вернет Response с токенами в JSON.
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
