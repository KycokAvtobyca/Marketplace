"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import include, path
from django.views import View
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from core import settings

# Переопределяем site_url админки на фронтенд
admin.site.site_url = "http://127.0.0.1:3000/"


class AdminAutoLoginView(View):
    def get(self, request):
        auth = JWTAuthentication()
        raw_token = request.COOKIES.get("access_token")
        if raw_token:
            try:
                validated_token = auth.get_validated_token(raw_token)
                user = auth.get_user(validated_token)
                if user.is_staff or user.is_superuser:
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                    return HttpResponseRedirect("/admin/")
            except Exception:
                pass
        return HttpResponseRedirect("/admin/login/?next=/admin/")


urlpatterns = [
    path("admin-login/", AdminAutoLoginView.as_view(), name="admin-auto-login"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    # Путь для скачивания самого файла схемы (yaml/json)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI:
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc UI (альтернатива):
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
