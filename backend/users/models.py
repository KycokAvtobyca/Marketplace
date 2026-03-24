from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.db.models.functions import Lower
from django.core.validators import MinLengthValidator
from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Номер телефона обязателен")

        user = self.model(phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        if not password:
            raise ValueError("Суперпользователь обязан иметь пароль")
        
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(unique=True, region="RU", verbose_name="Номер телефона")
    name = models.CharField(null=True, blank=True, max_length=99, validators=[MinLengthValidator(2)], verbose_name="Имя")
    last_name = models.CharField(null=True, blank=True, max_length=150, validators=[MinLengthValidator(2)], verbose_name="Фамилия")
    email = models.EmailField(null=True, blank=True, verbose_name="Электронная почта")
    address = models.TextField(null=True, blank=True, verbose_name="Адрес")
    address_data = models.JSONField(null=True, blank=True, help_text="Хранит fias_id, координаты, индекс и т.д.", verbose_name="Полная информация адреса")
    date_time_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания") # Должно быть в будущем неизменяемым полем
    date_time_update = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    # Обязательные поля для AbstractBaseUser и PermissionsMixin
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Статус персонала")

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["name", "last_name"]

    def __str__(self):
        return str(self.phone_number)
    
    def save(self, *args, **kwargs):
        if self.email and self.email.strip():
            self.email = self.email.strip().lower()
        else:
            self.email = None # Жестко блокируем пустые строки и сохраняем NULL

        if self.pk:
            old = type(self).objects.filter(pk=self.pk).only('date_time_create').first()

            if old and self.date_time_create != old.date_time_create:
                raise ValueError("Поле date_time_create нельзя изменять")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_time_create"]

        indexes = [
            models.Index(fields=["-date_time_create"], name="user_created_idx"),
            
            # Рекомендуется делать поиск сначала по фамилии
            # из-за объединения создания двух индексов.
            # Иначе как обычный поиск
            models.Index(fields=["last_name", "name"], name="user_name_idx"),
            models.Index(
                fields=["-date_time_create"],
                condition=models.Q(is_active=True, is_staff=True),
                name="active_staff_idx"
            )
        ]

        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_lower_email"
            )
        ]