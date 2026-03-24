from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = [
        "phone_number",
        "name",
        "last_name",
        "email",
        "address",
        "address_data",
    ]

    ordering = ('-date_time_create',)
    search_fields = ('phone_number', 'email', 'name', 'last_name')

    readonly_fields = ("date_time_create", "date_time_update", "last_login")

    # Доработать непосредственно момент создания и отображения кастомного пользователя
