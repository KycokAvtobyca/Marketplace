from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, SMSCode


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Написать самому

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    # 1. Поля, которые отображаются в общем списке пользователей
    list_display = (
        "phone_number",
        "name",
        "last_name",
        "middle_name",
        "is_staff",
        "is_active",
    )

    # 2. Поля, по которым можно искать (УБРАЛИ username)
    search_fields = (
        "phone_number",
        "name",
        "last_name",
        "middle_name",
        "email",
    )

    # 3. Сортировка по умолчанию
    ordering = ("-date_time_create",)

    # 4. Настройка экрана РЕДАКТИРОВАНИЯ существующего пользователя
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            "Персональная информация",
            {
                "fields": (
                    "name",
                    "last_name",
                    "middle_name",
                    "email",
                    "address",
                    "address_data",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login",)}),
        # Поля date_time_create и date_time_update добавлять сюда нельзя,
        # так как они auto_now / auto_now_add (Django сам их контролирует)
    )

    # 5. Настройка экрана СОЗДАНИЯ нового пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                # Используем phone_number вместо username.
                # Для стандартной формы создания нужны два поля пароля.
                "fields": ("phone_number", "name", "last_name"),
            },
        ),
    )

    readonly_fields = ("date_time_create", "date_time_update", "last_login")


admin.site.register(SMSCode)
