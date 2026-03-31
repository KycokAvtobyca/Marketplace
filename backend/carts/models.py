from catalog.models import ProductVariant
from common.models import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
    SiteConfiguration,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone
from marketing.models import PromoCode


class Cart(DateTimeCreateMixin, DateTimeUpdateMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    promocode = models.ForeignKey(
        PromoCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name="Примененный промокод",
    )

    @property
    def total_items_price(self):
        """Считает стоимость всех товаров без учета промокода."""
        # Используем генератор, чтобы избежать лишних N+1 запросов,
        # предполагая, что корзина загружается через prefetch_related('cart_items__product_variant')
        return sum(item.total_price for item in self.cart_items.all())

    @property
    def total_cost(self):
        """Считает финальную стоимость с учетом примененного промокода."""
        base_price = self.total_items_price
        if base_price <= 0:
            return 0

        # Если промокод есть, и он валиден по сумме
        if self.promocode and base_price >= self.promocode.min_amount:
            # Получаем глобальный лимит
            config = SiteConfiguration.load()
            max_discount_limit = base_price * config.max_discount_percentage

            if self.promocode.amount:
                proposed_discount = self.promocode.amount
            elif self.promocode.discount_percentage:
                proposed_discount = (
                    base_price * self.promocode.discount_percentage
                )
            else:
                proposed_discount = 0

            # Мы не можем дать скидку больше, чем разрешено конфигом
            actual_discount = min(proposed_discount, max_discount_limit)

            return max(1, base_price - actual_discount)

        return base_price

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         config = SiteConfiguration.load()
    #         self.max_percentage_can_use = config.max_discount_percentage

    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Корзина {self.user.phone_number} (ID: {self.pk})"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(DateTimeCreateMixin):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Корзина",
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_lines",
        verbose_name="Вариация товара",
    )
    quantity = models.PositiveIntegerField(
        "Количество", default=1, validators=[MaxValueValidator(999)]
    )

    @property
    def total_price(self):
        return self.quantity * self.product_variant.price

    def clean(self):
        super().clean()

        if self.quantity > self.product_variant.stock:
            raise ValidationError(
                f"Недостаточно товара. В наличии: {self.product_variant.stock}"
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Атомарно и быстро обновляем дату корзины
        type(self.cart).objects.filter(pk=self.cart_id).update(
            date_time_update=timezone.now()
        )

    def delete(self, *args, **kwargs):
        # Сохраняем ссылки до удаления объекта
        cart_class = type(self.cart)
        cart_id = self.cart_id

        super().delete(*args, **kwargs)

        # Обновляем дату корзины при удалении товара
        cart_class.objects.filter(pk=cart_id).update(
            date_time_update=timezone.now()
        )

    def __str__(self):
        return f"{self.product_variant.product.name} x {self.quantity}"

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product_variant"], name="unique_cart_variant"
            )
        ]
