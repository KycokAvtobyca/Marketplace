from catalog.models import Brand, Category, Product, ProductVariant
from common.models import DateTimeCreateMixin, DateTimeUpdateMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from users.models import UserSegment


class ProductTag(models.Model):
    pass


class MarketingQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        # Активны те, у которых:
        # 1. Стоит флаг is_active
        # 2. Дата начала <= сейчас
        # 3. Дата окончания либо не задана (null), либо >= сейчас
        return self.filter(
            models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=now),
            is_active=True,
            valid_from__lte=now,
        )


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
    TARGET_FIELDS = [
        "user",
        "segment",
        "product_variant",
        "product",
        "tag",
        "brand",
        "category",
    ]

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
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На категорию",
        help_text="Приоритет 2",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На бренд",
        help_text="Приоритет 3",
    )
    tag = models.ForeignKey(
        ProductTag,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На тег (подборку)",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На товар",
        help_text="Приоритет 4",
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На вариацию товара (SKU)",
        help_text="Приоритет 5",
    )
    segment = models.ForeignKey(
        UserSegment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На сегмент пользователей",
        help_text="Приоритет 6",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="На пользователя",
        help_text="Приоритет 7",
    )

    # Исключения
    excluded_categories = models.ManyToManyField(
        Category,
        blank=True,
        verbose_name="Исключить категории",
        related_name="%(class)s_excluded",
    )
    excluded_brands = models.ManyToManyField(
        Brand,
        blank=True,
        verbose_name="Исключить бренды",
        related_name="%(class)s_excluded",
    )
    excluded_tags = models.ManyToManyField(
        "ProductTag",
        blank=True,
        verbose_name="Исключить теги",
        related_name="%(class)s_excluded",
    )
    excluded_products = models.ManyToManyField(
        Product,
        blank=True,
        verbose_name="Исключить товары",
        related_name="%(class)s_excluded",
    )
    excluded_variants = models.ManyToManyField(
        ProductVariant,
        blank=True,
        verbose_name="Исключить вариации",
        related_name="%(class)s_excluded",
    )
    excluded_segments = models.ManyToManyField(
        UserSegment,
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

    def save(self, *args, **kwargs):
        priority_choices = type(self).Priority

        # Сначала обрабатываем самый низкий приоритет (глобальный)
        if self.is_global:
            self.priority = priority_choices.GLOBAL
        else:
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
                    self.priority = mapping.get(field)
                    break

        super().save(*args, **kwargs)

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

        # Определяем список полей, которые должны быть взаимоисключающими
        target_fields = [
            "category",
            "brand",
            "tag",
            "product",
            "product_variant",
            "segment",
            "user",
        ]

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

        constraints = [
            models.CheckConstraint(
                condition=(
                    cond_global
                    | (models.Q(is_global=False) & exactly_one_check)
                ),
                name="%(app_label)s_%(class)s_exactly_one_target",
            )
        ]


class Discount(MarketingBase):
    name = models.CharField("Название акции", blank=True, max_length=99)
    description = models.TextField(
        "Описание акции", blank=True, max_length=3000
    )
    can_use_with_promocode = models.BooleanField(
        "Можно ли использовать с промокодом", default=False, blank=True
    )

    def __str__(self):
        return f"Акция {self.name} с приоритетом {self.priority}"

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"


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

    def clean(self):
        super().clean()

        # Гарантируем, что заполнено только что-то одно
        has_percentage = self.discount_percentage > 0
        has_amount = self.amount is not None and self.amount > 0

        if has_percentage and has_amount:
            raise ValidationError(
                "Промокод не может одновременно иметь процентную скидку и фиксированную сумму. Выберите что-то одно."
            )

        if not has_percentage and not has_amount:
            raise ValidationError("Укажите размер скидки (процент или сумму).")

    def can_use(self, user):
        """Проверка возможности использования"""

        now = timezone.now()

        if not self.is_active:
            return False

        if self.valid_from and now < self.valid_from:
            return False

        if self.valid_to and now > self.valid_to:
            return False

        if self.current_usage >= self.usage_limit:
            return False
        return True

    def use(self):
        """Атомарное использование промокода"""
        # refreshed_self = type(self).objects.select_for_update().get(pk=self.pk)
        # if refreshed_self.current_usage < refreshed_self.usage_limit:
        #     refreshed_self.current_usage += 1
        #     refreshed_self.save()
        #     return True
        # return False

        updated_count = (
            type(self)
            .objects.filter(
                pk=self.pk, current_usage__lt=models.F("usage_limit")
            )
            .update(current_usage=models.F("current_usage") + 1)
        )

        return updated_count > 0

    def __str__(self):
        return f"Промокод {self.code} с приоритетом {self.priority}"

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
