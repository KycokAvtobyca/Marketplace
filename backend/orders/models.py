from datetime import timedelta
from decimal import Decimal

from common.mixins import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
)
from common.models import SiteConfiguration
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


def get_default_valid_to():
    future_date = timezone.now() + timedelta(days=10)

    # microsecond=0 важно, чтобы в базе не было лишних долей секунды
    return future_date.replace(hour=23, minute=59, second=59, microsecond=0)


# В Корзине: total_cost — это динамический @cached_property.
# В Заказе: total_cost — это поле в БД (DecimalField).
class Order(DateTimeCreateMixin, DateTimeUpdateMixin):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Создан (Не оплачен)"
        PAID = "PAID", "Оплачен (В обработке)"
        ASSEMBLING = "ASSEMBLING", "Собирается"
        DELIVERING = "DELIVERING", "В пути / Готов к выдаче"
        COMPLETED = "COMPLETED", "Выполнен"
        CANCELED = "CANCELED", "Отменен"

    class DeliveryType(models.TextChoices):
        PICKUP = "PICKUP", "Самовывоз"
        COURIER = "COURIER", "Курьерская доставка"

    class PickUpBranches(models.TextChoices):
        # Храним короткий код в БД, а длинный текст показываем людям
        LENINA_5A = "LENINA_5A", "г. Иркутск, ул. Ленина, д. 5А"

    # Основная информация
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
        verbose_name="Пользователь",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.CREATED
    )

    # Товары
    items = models.ManyToManyField(
        "catalog.ProductVariant",
        through="OrderItem",
        related_name="orders",
        verbose_name="Товары в заказе",
    )

    # Контакты
    name = models.CharField(
        "Имя получателя", max_length=99, validators=[MinLengthValidator(2)]
    )
    phone_number = PhoneNumberField(region="RU", verbose_name="Номер телефона")

    # Логистика
    delivery_type = models.CharField(
        "Тип доставки", max_length=20, choices=DeliveryType.choices
    )
    date_time_deliver = models.DateTimeField(
        "К какому сроку нужно доставить", default=get_default_valid_to
    )

    branch = models.CharField(
        "Пункт выдачи",
        max_length=50,
        choices=PickUpBranches.choices,
        blank=True,
        null=True,
    )
    address = models.TextField("Адрес доставки", blank=True, null=True)
    address_data = models.JSONField(
        "Данные адреса (FIAS/Координаты)", blank=True, null=True
    )

    description = models.TextField(
        "Примечание к заказу", max_length=2000, blank=True
    )

    # Финансы и маркетинг
    total_cost_without_sales = models.DecimalField(
        "Сумма без скидок",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_cost = models.DecimalField(
        "Итоговая стоимость",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    discount = models.ForeignKey(
        "marketing.Discount",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Акция",
    )
    promocode = models.ForeignKey(
        "marketing.PromoCode",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Промокод",
    )
    max_percentage_can_use = models.DecimalField(
        "Максимальный процент скидки (снимок)",
        max_digits=3,
        decimal_places=2,
        editable=False,  # Скрываем в админке, так как это системный лог
        help_text="Лимит скидки, действовавший в момент создания заказа",
        null=True,  # Позволяем null, чтобы не было ошибок до первого сохранения
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-date_time_create"]

        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "delivery_type"]),
            models.Index(fields=["phone_number"]),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_cost__gte=0)
                & models.Q(total_cost_without_sales__gte=0),
                name="check_positive_costs",
            ),
            # Гарантируем, что нужные поля заполнены в зависимости от типа доставки
            models.CheckConstraint(
                condition=(
                    models.Q(delivery_type="PICKUP")
                    & models.Q(branch__isnull=False)
                    & models.Q(address__isnull=True)
                    | (
                        models.Q(delivery_type="COURIER")
                        & models.Q(address__isnull=False)
                        & models.Q(branch__isnull=True)
                    )
                ),
                name="check_delivery_fields_integrity",
            ),
        ]

    def get_base_price_for_promocode(self):
        """
        Вычисляет сумму, на которую смотрит промокод.
        Это сумма до вычета самого промокода, но с учетом акций.
        """
        base = self.total_cost_without_sales

        if self.discount:
            if self.discount.discount_percentage:
                base -= base * self.discount.discount_percentage

        return base

    def clean(self):
        super().clean()

        # Валидация маркетинга
        if self.discount_id and self.promocode_id:
            if not self.discount.can_use_with_promocode:
                raise ValidationError(
                    {
                        "promocode": "С данной акцией нельзя использовать промокод"
                    }
                )

        if self.total_cost > self.total_cost_without_sales:
            raise ValidationError(
                {
                    "total_cost": "Итоговая цена не может быть больше суммы без скидок."
                }
            )

        if self.promocode:
            self.promocode.can_use(
                user=self.user, order_total=self.get_base_price_for_promocode()
            )

        # Валидация логистики на уровне Python
        if self.delivery_type == self.DeliveryType.PICKUP and not self.branch:
            raise ValidationError(
                {"branch": "Для самовывоза необходимо указать пункт выдачи."}
            )

        if self.delivery_type == self.DeliveryType.COURIER and not self.address:
            raise ValidationError(
                {"address": "Для доставки курьером необходимо указать адрес."}
            )

    def save(self, *args, **kwargs):
        if not self.pk:
            config = SiteConfiguration.load()
            self.max_percentage_can_use = config.max_discount_percentage

        if self.promocode:
            self.promocode.can_use(
                user=self.user, order_total=self.get_base_price_for_promocode()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.pk} ({self.get_status_display()}) - {self.phone_number}"


class OrderItem(DateTimeCreateMixin):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product_variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(
        "Количество", validators=[MinValueValidator(1)]
    )

    # Исторический снимок финансов
    price_per_item = models.DecimalField(
        "Цена за 1 шт. на момент покупки", max_digits=10, decimal_places=2
    )
    discounted_price_per_item = models.DecimalField(
        "Цена за 1 шт. со скидкой", max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

        constraints = [
            # Один и тот же вариант товара не должен дублироваться в одном заказе отдельными строками
            models.UniqueConstraint(
                fields=["order", "product_variant"],
                name="unique_variant_per_order",
            )
        ]

    def __str__(self):
        return (
            f"{self.quantity} x {self.product_variant} (Заказ #{self.order_id})"
        )

    # Только для FrontEnd
    @property
    def total_price(self):
        return self.quantity * self.discounted_price_per_item
