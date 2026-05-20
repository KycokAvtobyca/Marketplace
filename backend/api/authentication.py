from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import PhoneBan


class HttpOnlyJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token") or None

        print(f"DEBUG COOKIES: {request.COOKIES}")

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            if not user.is_active:
                raise AuthenticationFailed(
                    {
                        "message": "Ваш аккаунт заблокирован.",
                        "code": "user_blocked",
                    },
                    code="user_blocked",
                )
            if PhoneBan.is_phone_banned(user.phone_number):
                raise AuthenticationFailed(
                    {
                        "message": "Ваш номер телефона заблокирован.",
                        "code": "user_blocked",
                    },
                    code="user_blocked",
                )
            return user, validated_token
        except AuthenticationFailed:
            raise
        except Exception:
            # Если токен протух, DRF вернет 401
            return None
