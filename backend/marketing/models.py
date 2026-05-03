from common.mixins import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from .managers import MarketingQuerySet

MARKETING_TARGET_FIELDS = [
    "user",
    "segment",
    "product_variant",
    "product",
    "tag",
    "brand",
    "category",
]


def get_marketing_constraints():
    target_fields = MARKETING_TARGET_FIELDS

    # Если is_global=True, все target_fields должны быть null
    cond_global = models.Q(is_global=True)
    for field in target_fields:
        cond_global &= models.Q(**{f"{field}__isnull": True})

    # Если is_global=False, ровно ОДИН target_field не null
    exactly_one_check = models.Q()
    for field in target_fields:
        # Создаем условие, где текущее поле не null
        cond = models.Q(**{f"{field}__isnull": False})

        # А все остальные поля - null
        for other in target_fields:
            if other != field:
                cond &= models.Q(**{f"{other}__isnull": True})

        exactly_one_check |= cond

    return cond_global | (models.Q(is_global=False) & exactly_one_check)


class MarketingBase(DateTimeCreateMixin, DateTimeUpdateMixin):
    class Priority(models.IntegerChoices):
        NULL = 0, "Не задан"
        GLOBAL = 1, "На все (Глобальная)"
        CATEGORY = 2, "На категорию"
        BRAND = 3, "На бренд"
        TAG = 4, "На тег (подборку)"
        PRODUCT = 5, "На товар"
        VARIANT = 6, "На вариацию товара (SKU)"
        SEGMENT = 7, "На сегмент пользователей"
        USER = 8, "На конкретного пользователя"

    # Константа со списком полей в порядке приоритета (от высшего к низшему)
    # Это позволит нам не хардкодить списки в методах
    TARGET_FIELDS = MARKETING_TARGET_FIELDS

    objects = MarketingQuerySet.as_manager()

    priority = models.PositiveSmallIntegerField(
        "Приоритет",
        choices=Priority.choices,
        default=Priority.NULL,
        help_text="Определяется автоматически в зависимости от цели акции",
        editable=False,
    )
    is_global = models.BooleanField(
        "На все",
        default=False,
        help_text="Приоритет 1 (Глобальная скидка)",
    )
    is_active = models.BooleanField("Активна ли", default=False, blank=True)
    valid_from = models.DateTimeField("Дата начала", default=timezone.now)
    valid_to = models.DateTimeField("Дата окончания", null=True, blank=True)
    discount_percentage = models.DecimalField(
        "Процент скидки",
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Значение от 0.00 до 1.00 (например, 0.15 — это скидка 15%)",
    )

    # Целевые поля
    category = models.ForeignKey(
        "catalog.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На категорию",
        help_text="Приоритет 2",
    )
    brand = models.ForeignKey(
        "catalog.Brand",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На бренд",
        help_text="Приоритет 3",
    )
    tag = models.ForeignKey(
        "catalog.ProductTag",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На тег (подборку)",
        help_text="Приоритет 4",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На товар",
        help_text="Приоритет 5",
    )
    product_variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На вариацию товара (SKU)",
        help_text="Приоритет 6",
    )
    segment = models.ForeignKey(
        "users.UserSegment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На сегмент пользователей",
        help_text="Приоритет 7",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На пользователя",
        help_text="Приоритет 8",
    )

    # Исключения
    excluded_categories = models.ManyToManyField(
        "catalog.Category",
        blank=True,
        verbose_name="Исключить категории",
        related_name="%(class)s_excluded",
    )
    excluded_brands = models.ManyToManyField(
        "catalog.Brand",
        blank=True,
        verbose_name="Исключить бренды",
        related_name="%(class)s_excluded",
    )
    excluded_tags = models.ManyToManyField(
        "catalog.ProductTag",
        blank=True,
        verbose_name="Исключить теги",
        related_name="%(class)s_excluded",
    )
    excluded_products = models.ManyToManyField(
        "catalog.Product",
        blank=True,
        verbose_name="Исключить товары",
        related_name="%(class)s_excluded",
    )
    excluded_variants = models.ManyToManyField(
        "catalog.ProductVariant",
        blank=True,
        verbose_name="Исключить вариации",
        related_name="%(class)s_excluded",
    )
    excluded_segments = models.ManyToManyField(
        "users.UserSegment",
        blank=True,
        verbose_name="Исключить сегменты",
        related_name="%(class)s_excluded",
    )
    excluded_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name="Исключить пользователей",
        related_name="%(class)s_excluded",
    )

    class Meta:
        abstract = True

        indexes = [
            models.Index(
                fields=["is_active", "valid_from", "valid_to"],
                name="%(class)s_active_idx",
            ),
            models.Index(
                fields=["is_active", "priority"],
                name="%(class)s_active_priority_idx",
            ),
            models.Index(fields=["is_global"], name="%(class)s_global_idx"),
        ]

        constraints = [
            models.CheckConstraint(
                condition=get_marketing_constraints(),
                name="%(app_label)s_%(class)s_exactly_one_target",
            )
        ]

    def clean(self):
        super().clean()

        filled_targets = sum(
            1
            for field in self.TARGET_FIELDS
            if getattr(self, f"{field}_id", None)
        )

        if self.is_global:
            if filled_targets > 0:
                raise ValidationError(
                    "Если выбрана опция скидка «На все», целевые поля (категория, товар и т.д.) должны быть пустыми. Используйте поля исключений."
                )
        else:
            if filled_targets == 0:
                raise ValidationError(
                    "Выберите хотя бы один объект для применения скидки (или поставьте галочку «На все»)."
                )
            if filled_targets > 1:
                raise ValidationError(
                    "Точечная скидка может быть привязана только к одному объекту (либо категория, либо товар и т.д.)."
                )

    def calculate_priority(self):
        priority_choices = type(self).Priority

        mapping = {
            "user": priority_choices.USER,
            "segment": priority_choices.SEGMENT,
            "product_variant": priority_choices.VARIANT,
            "product": priority_choices.PRODUCT,
            "tag": priority_choices.TAG,
            "brand": priority_choices.BRAND,
            "category": priority_choices.CATEGORY,
        }

        # Ищем первое заполненное поле из нашего списка приоритетов

        for field in self.TARGET_FIELDS:
            if getattr(self, f"{field}_id", None):
                return mapping.get(field)

    def save(self, *args, **kwargs):
        priority_choices = type(self).Priority

        # Сначала обрабатываем самый низкий приоритет (глобальный)
        if self.is_global:
            self.priority = priority_choices.GLOBAL
        else:
            self.priority = self.calculate_priority()

        super().save(*args, **kwargs)


class Discount(MarketingBase):
    name = models.CharField("Название акции", blank=True, max_length=99)
    description = models.TextField(
        "Описание акции", blank=True, max_length=3000
    )
    can_use_with_promocode = models.BooleanField(
        "Можно ли использовать с промокодом", default=False, blank=True
    )

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return f"Акция {self.name} с приоритетом {self.priority}"


class PromoCode(MarketingBase):
    code = models.CharField(
        "Промокод",
        max_length=20,
        unique=True,
        validators=[MinLengthValidator(3)],
    )
    description = models.TextField(
        "Описание промокода", blank=True, max_length=3000
    )
    usage_limit = models.PositiveIntegerField("Макс. использований", default=1)
    current_usage = models.PositiveIntegerField(
        "Уже использовано", default=0, editable=False
    )
    min_amount = models.DecimalField(
        "Минимальная сумма заказа",
        max_digits=10,
        decimal_places=2,
        default=10,
        validators=[MinValueValidator(10)],
    )
    amount = models.DecimalField(
        "Сумма скидки",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Оставьте пустым, если используете 'Процент скидки'",
    )

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

        constraints = [
            models.CheckConstraint(
                condition=(
                    # ВАРИАНТ А: Есть процент, нет фиксированной суммы
                    (
                        models.Q(discount_percentage__gt=0)
                        & (models.Q(amount__isnull=True) | models.Q(amount=0))
                    )
                    |
                    # ВАРИАНТ Б: Нет процента, есть фиксированная сумма
                    (models.Q(discount_percentage=0) & models.Q(amount__gt=0))
                ),
                name="%(app_label)s_%(class)s_exclusive_discount_type",
            )
        ]

    def __str__(self):
        return f"Промокод {self.code} с приоритетом {self.priority}"

    def can_use_check(self, user=None, order_total=None):
        """Проверка возможности использования"""

        now = timezone.now()

        not_active_err = "Промокод больше не активен."
        doesnt_have = "Промокод не существует."

        # Базовые системные проверки (самые быстрые)
        if not self.is_active:
            return False, not_active_err

        if self.valid_from and now < self.valid_from:
            return False, not_active_err

        if self.valid_to and now > self.valid_to:
            return False, doesnt_have

        # Общий лимит использований (глобальный счетчик)
        if self.current_usage >= self.usage_limit:
            return (
                False,
                "Количество использований промокода достигло максимума.",
            )

        # Проверка суммы корзины/заказа (Инкапсуляция логики)
        if (
            order_total is not None
            and self.min_amount
            and order_total < self.min_amount
        ):
            return (
                False,
                f"Этот промокод действует при сумме от {self.min_amount} руб.",
            )

        # Проверять можно ли использовать с текущей акцией

        # Персональные ограничения (User / Segment)
        # Если в промокоде указан целевой пользователь или сегмент
        if self.user_id or self.segment_id:
            # Если код персональный, а пользователя нам не передали или он аноним - отказ
            if not user or not user.is_authenticated:
                return False, "Войдите в систему, чтобы применить промокод."

            # Проверка: Личный промокод (Priority 8)
            # Сравниваем ID напрямую, чтобы не дергать объект из базы лишний раз
            if self.user_id and self.user_id != user.id:
                return False, doesnt_have

            # Проверка: Сегмент пользователей (Priority 7)
            if self.segment_id:
                # Проверяем, входит ли наш пользователь в нужный сегмент
                # Используем .exists(), это самый быстрый способ проверить связь в БД
                if not user.segments.filter(id=self.segment_id).exists():
                    return False, doesnt_have

        # 4. Проверка "Один раз в одни руки"
        # Персональные промокоды нельзя использовать дважды одному и тому же человеку.
        if user and user.is_authenticated:
            # Импортируем модель заказа внутри метода, чтобы избежать кольцевого импорта
            from orders.models import Order

            # Если пользователь уже имеет завершенный или оплаченный заказ с этим промокодом
            user_already_used = (
                Order.objects.filter(user=user, promocode=self)
                .exclude(status=Order.Status.CANCELED)
                .values("pk")
                .exists()
            )

            if user_already_used:
                return False, "Вы уже использовали данный промокод."

        return True, ""

    def can_use(self, user=None, order_total=None):
        """
        Метод-обертка для вызова валидации.
        Выбрасывает исключение, если что-то не так.
        """
        is_valid, err_msg = self.can_use_check(
            user=user, order_total=order_total
        )
        if not is_valid:
            raise ValidationError({"promocode": err_msg})

    def use(self):
        """Атомарное использование промокода"""
        updated_count = (
            type(self)
            .objects.filter(
                pk=self.pk, current_usage__lt=models.F("usage_limit")
            )
            .update(current_usage=models.F("current_usage") + 1)
        )

        return updated_count > 0

    def clean(self):
        super().clean()

        if not self.user_id:
            raise ValidationError({"user": "Пользователен должен быть указан."})

        # Гарантируем, что заполнено только что-то одно
        has_percentage = self.discount_percentage > 0
        has_amount = self.amount is not None and self.amount > 0

        if has_percentage and has_amount:
            raise ValidationError(
                "Промокод не может одновременно иметь процентную скидку и фиксированную сумму. Выберите что-то одно."
            )

        if not has_percentage and not has_amount:
            raise ValidationError("Укажите размер скидки (процент или сумму).")
