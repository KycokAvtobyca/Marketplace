"""
API Views для различных операций.
"""
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.admin_auth import JWTAdminAuthBackend


@require_http_methods(["POST"])
@csrf_exempt
def admin_redirect(request):
    """
    Перенаправляет пользователя в Django админку.
    
    Аутентифицирует пользователя по JWT токену из cookies и создает сессию
    для входа в админку.
    
    Returns:
        - JSON с URL админки, если токен валиден и пользователь is_staff
        - JSON ошибка, если не авторизован
    """
    backend = JWTAdminAuthBackend()
    user = backend.authenticate(request)

    if user is None:
        return JsonResponse(
            {"error": "Не авторизован или нет доступа к админке"},
            status=403
        )

    # Создаем сессию для входа в админку
    login(request, user, backend="core.admin_auth.JWTAdminAuthBackend")

    # Возвращаем абсолютный URL админки
    admin_url = request.build_absolute_uri("/admin/")
    return JsonResponse({"admin_url": admin_url})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_admin_access(request):
    """
    Проверяет, есть ли у пользователя доступ к админке.
    
    Returns:
        - {"has_access": true/false}
    """
    has_access = request.user.is_staff or request.user.is_superuser
    return Response({"has_access": has_access})

