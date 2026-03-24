from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

# Создать свои формы без наследования от стандартного пользователя
class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model=CustomUser
        fields=("phone_number",)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model=CustomUser
        fields=("phone_number", "name", "last_name", "email")