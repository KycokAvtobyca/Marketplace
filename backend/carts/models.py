from common.mixins import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
)
from common.models import SiteConfiguration
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property


class Cart(DateTimeCreateMixin, DateTimeUpdateMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    promocode = models.ForeignKey(
        "marketing.PromoCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name="Примененный промокод",
    )
    items = models.ManyToManyField(
        "catalog.ProductVariant",
        through="CartItem",
        related_name="carts",
        verbose_name="Товары в корзине",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user.phone_number} (ID: {self.pk})"

    # Считать также с точечной скидкой
    @cached_property
    def total_items_price(self):
        """Считает стоимость всех товаров без учета промокода, но с учетом всех скидок."""
        # Используем генератор, чтобы избежать лишних N+1 запросов,
        # предполагая, что корзина загружается через prefetch_related('cart_items__product_variant')
        return sum(item.total_price for item in self.cart_items.all())

    @cached_property
    def total_cost(self):
        """Считает финальную стоимость с учетом примененного промокода."""
        base_price = self.total_items_price
        if base_price <= 0:
            return 0

        # Если промокод есть и он валиден по сумме
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

            # Гарантируем, что цена заказа не упадет ниже 1 рубля
            return max(1, base_price - actual_discount)

        return base_price

    def clear_cache(self):
        """Принудительный сброс закэшированных расчетов."""
        # Проверяем, есть ли значение в кэше, чтобы не получить AttributeError
        for prop in ["total_items_price", "total_cost"]:
            if prop in self.__dict__:
                del self.__dict__[prop]

    # Финальная стоимость с учетом
    def clean(self):
        super().clean()

        if self.promocode:
            self.promocode.can_use(
                user=self.user, order_total=self.total_items_price
            )

    def save(self, *args, **kwargs):
        if self.promocode:
            self.promocode.can_use(
                user=self.user, order_total=self.total_items_price
            )

        super().save(*args, **kwargs)


class CartItem(DateTimeCreateMixin):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Корзина",
    )
    product_variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        related_name="cart_lines",
        verbose_name="Вариация товара",
    )
    quantity = models.PositiveIntegerField(
        "Количество", default=1, validators=[MaxValueValidator(999)]
    )

    # Пример того, как нужно загружать корзину в будущем:
    # cart = Cart.objects.prefetch_related(
    #     Prefetch(
    #         'cart_items__product_variant',
    # Принудительно заставляем ORM посчитать скидки для товаров в корзине
    #         queryset=ProductVariant.objects.with_prices(user=request.user)
    #     )
    # ).get(user=request.user)

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product_variant"], name="unique_cart_variant"
            )
        ]

    def __str__(self):
        return f"{self.product_variant.product.name} x {self.quantity}"

    @property
    def total_price(self):
        # Учитываем глобальные скидки
        return self.quantity * self.product_variant.final_price

    def clean(self):
        super().clean()

        if self.quantity > self.product_variant.stock:
            raise ValidationError(
                f"Недостаточно товара. В наличии: {self.product_variant.stock}"
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.cart:
            self.cart.clear_cache()

        # Атомарно и быстро обновляем дату корзины
        Cart.objects.filter(pk=self.cart_id).update(
            date_time_update=timezone.now()
        )

    def delete(self, *args, **kwargs):
        if self.cart:
            self.cart.clear_cache()

        # Сохраняем ссылки до удаления объекта
        cart_id = self.cart_id

        super().delete(*args, **kwargs)

        # Обновляем дату корзины без лишних запросов за объектом
        if cart_id:
            Cart.objects.filter(pk=cart_id).update(
                date_time_update=timezone.now()
            )
