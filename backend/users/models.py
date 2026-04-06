from common.models import DateTimeCreateMixin, DateTimeUpdateMixin
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.functions import Lower
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


class CustomUser(
    AbstractBaseUser, PermissionsMixin, DateTimeCreateMixin, DateTimeUpdateMixin
):
    phone_number = PhoneNumberField(
        unique=True, region="RU", verbose_name="Номер телефона"
    )
    name = models.CharField(
        blank=True,
        max_length=99,
        validators=[MinLengthValidator(2)],
        verbose_name="Имя",
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        validators=[MinLengthValidator(2)],
        verbose_name="Фамилия",
    )
    middle_name = models.CharField(
        blank=True,
        max_length=150,
        validators=[MinLengthValidator(2)],
        verbose_name="Отчество",
    )
    email = models.EmailField(
        null=True, blank=True, verbose_name="Электронная почта"
    )
    address = models.TextField(blank=True, verbose_name="Адрес")
    address_data = models.JSONField(
        blank=True,
        default=dict,
        help_text="Хранит fias_id, координаты, индекс и т.д.",
        verbose_name="Полная информация адреса",
    )

    # Обязательные поля для AbstractBaseUser и PermissionsMixin
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(
        default=False, verbose_name="Статус персонала"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["name", "last_name"]

    def can_add_review(self, variant):
        """
        Проверяет, может ли пользователь оставить отзыв на конкретный SKU.
        """

        from orders.models import Order, OrderItem

        return OrderItem.objects.filter(
            order__user_id=self.user.id,
            product_variant_id=variant.pk,
            order__status=Order.Status.COMPLETED,
        ).exists()

    def __str__(self):
        return str(self.phone_number)

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower() or None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_time_create"]

        indexes = [
            # models.Index(fields=["-date_time_create"], name="user_created_idx"),
            # Рекомендуется делать поиск сначала по фамилии
            # из-за объединения создания двух индексов.
            # Иначе как обычный поиск
            models.Index(
                fields=["last_name", "name", "middle_name"],
                name="user_name_idx",
            ),
            models.Index(
                fields=["-date_time_create"],
                condition=models.Q(is_active=True, is_staff=True),
                name="active_staff_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(Lower("email"), name="unique_lower_email")
        ]


class UserSegment(models.Model):
    name = models.CharField("Название сегмента", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True, max_length=500)

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="segments",
        blank=True,
        verbose_name="Пользователи в сегменте",
    )

    is_active = models.BooleanField("Активен", default=True)
    is_automated = models.BooleanField(
        "Автоматический сегмент",
        default=False,
        help_text="Если True, сегмент наполняется фоновыми задачами (например, рассылка)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Сегмент пользователей"
        verbose_name_plural = "Сегменты пользователей"


class SMSCode(DateTimeCreateMixin):
    phone_number = PhoneNumberField(
        unique=True, region="RU", verbose_name="Номер телефона"
    )
    code = models.CharField(max_length=6, verbose_name="СМС-код")

    def __str__(self):
        return f"СМС-код для {self.phone_number}"

    class Meta:
        verbose_name = "СМС-код"
        verbose_name_plural = "СМС-кода"
