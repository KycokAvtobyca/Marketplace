from common.mixins import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
)
from common.models import SiteConfiguration
from decimal import Decimal
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

    # Считает также с точечной скидкой
    def get_total_items_price(self, cart_items=None):
        items = cart_items if cart_items is not None else self.cart_items.all()
        return sum(item.total_price for item in items)

    def get_promocode_eligible_total(self, cart_items=None):
        if not self.promocode:
            return Decimal("0.00")

        items = cart_items if cart_items is not None else self.cart_items.all()
        return self.promocode.get_eligible_total(items, user=self.user)

    def calculate_total_cost(self, cart_items=None):
        base_price = self.get_total_items_price(cart_items)
        if base_price <= 0:
            return Decimal("0.00")

        eligible_price = self.get_promocode_eligible_total(cart_items)
        if (
            not self.promocode
            or eligible_price <= 0
            or eligible_price < self.promocode.min_amount
        ):
            return base_price

        config = SiteConfiguration.load()
        max_discount_limit = eligible_price * Decimal(
            str(config.max_discount_percentage)
        )

        if self.promocode.amount:
            proposed_discount = self.promocode.amount
        elif self.promocode.discount_percentage:
            proposed_discount = eligible_price * Decimal(
                str(self.promocode.discount_percentage)
            )
        else:
            proposed_discount = Decimal("0.00")

        actual_discount = min(proposed_discount, max_discount_limit, eligible_price)
        return max(Decimal("1.00"), base_price - actual_discount)

    @cached_property
    def total_items_price(self):
        """Считает стоимость всех товаров без учета промокода, но с учетом всех скидок."""
        # Используем генератор, чтобы избежать лишних N+1 запросов,
        return self.get_total_items_price()

    @cached_property
    def total_cost(self):
        return self.calculate_total_cost()

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
                user=self.user,
                order_total=self.get_promocode_eligible_total(),
            )

    def save(self, *args, **kwargs):
        if self.promocode:
            self.promocode.can_use(
                user=self.user,
                order_total=self.get_promocode_eligible_total(),
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
