"""
Кастомный бэкенд аутентификации для Django админки.
Проверяет JWT токены из фронтенда.
"""
from django.contrib.auth.backends import ModelBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from users.models import CustomUser


class JWTAdminAuthBackend(ModelBackend):
    """
    Бэкенд для аутентификации в Django админке через JWT токены.
    Используется для входа с фронтенда в админку без ввода пароля.
    """

    def authenticate(self, request, token=None, **kwargs):
        """
        Аутентифицирует пользователя по JWT токену.
        
        Args:
            request: HTTP запрос
            token: JWT токен из параметра или cookies
        
        Returns:
            Пользователь если токен валиден, иначе None
        """
        if token is None:
            # Пытаемся получить токен из cookies
            token = request.COOKIES.get("access_token")

        if token is None:
            return None

        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            
            # Проверяем, что пользователь имеет доступ к админке
            if user and (user.is_staff or user.is_superuser):
                return user
            
            return None
        except (InvalidToken, TokenError, CustomUser.DoesNotExist):
            return None

    def get_user(self, user_id):
        """Получить пользователя по ID."""
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
