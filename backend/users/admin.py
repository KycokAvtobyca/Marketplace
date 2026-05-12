from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Shop, SMSCode


@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
        "phone_number",
        "name",
        "is_active",
        "is_staff",
        "date_time_create",
    )

    search_fields = (
        "phone_number",
        "name",
        "email",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "date_time_create",
    )

    ordering = ("-date_time_create",)
    list_per_page = 25
    date_hierarchy = "date_time_create"

    readonly_fields = ("date_time_create", "date_time_update", "last_login")

    def get_fieldsets(self, request, obj=None):
        """Убрать раздел пароля для не-суперпользователей."""
        fieldsets = super().get_fieldsets(request, obj)
        
        # Скрываем пароль если редактируем не-суперпользователя
        if obj is not None and not obj.is_superuser:
            fieldsets = [
                (name, opts) for name, opts in fieldsets
                if name != 'Password'
            ]
        
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """Убрать поле пароля из формы для не-суперпользователей."""
        form = super().get_form(request, obj, **kwargs)
        
        # Убираем поле пароля если редактируем не-суперпользователя
        if obj is not None and not obj.is_superuser:
            # Удаляем из fields если есть
            if hasattr(form, 'fields') and 'password' in form.fields:
                del form.fields['password']
            # Также удаляем из base_fields для инстанце проверок
            if hasattr(form, 'base_fields') and 'password' in form.base_fields:
                form.base_fields = {k: v for k, v in form.base_fields.items() if k != 'password'}
        
        return form


@admin.register(Shop)
class ShopAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "owner",
        "is_active",
        "data_time_create",
    )

    search_fields = ("name", "owner__name", "owner__phone_number")

    list_filter = ("is_active", "data_time_create")

    readonly_fields = ("data_time_create",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20


@admin.register(SMSCode)
class SMSCodeAdmin(ImportExportModelAdmin):
    list_display = (
        "phone_number",
        "code",
        "date_time_create",
    )

    search_fields = ("phone_number",)

    list_filter = ("date_time_create",)

    readonly_fields = ("phone_number", "code", "date_time_create")
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
