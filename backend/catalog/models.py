import uuid

from common.models import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
    SingleMainMixin,
    SlugifiedNameMixin,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
)
from django.db import IntegrityError, models, transaction


# --- Базовые справочники ---
class Category(SlugifiedNameMixin):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Brand(models.Model):
    name = models.CharField(
        "Бренд", max_length=50, validators=[MinLengthValidator(2)], unique=True
    )
    description = models.TextField(
        "Описание бренда", max_length=5000, blank=True
    )

    # Добавить фотографию

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"


# Категория свойства, то что вообще бывает.
# Например: Цвет, Размер
class Attribute(models.Model):
    name = models.CharField(
        "Название атрибута",
        unique=True,
        max_length=99,
        validators=[MinLengthValidator(2)],
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"


# ------


# Конкретное значение свойства
# Красный, XL, Кожа
class AttributeValue(models.Model):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, verbose_name="Атрибут"
    )
    value = models.CharField(
        "Значение атрибута", max_length=50, validators=[MinLengthValidator(2)]
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"

        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"], name="unique_attribute_value"
            )
        ]


# Общая карточка
class Product(DateTimeCreateMixin, DateTimeUpdateMixin, SlugifiedNameMixin):
    description = models.TextField(
        "Описание товара",
        max_length=4000,
        blank=True,
        validators=[MinLengthValidator(10)],
    )
    views = models.PositiveIntegerField("Просмотры", default=0, editable=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Бренд",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Продавец",
        related_name="products",
    )

    # Добавить скидку

    # Обновляется через DRF или админку
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Кто последний обновил",
        related_name="updated_products",
        editable=False,
    )
    attributes = models.ManyToManyField(
        Attribute, verbose_name="Доступные атрибуты", blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.pk})"

    class Meta:
        verbose_name = "Товар (карточка)"
        verbose_name_plural = "Товары (карточки)"

        indexes = [
            models.Index(
                fields=["-date_time_create"], name="product_created_idx"
            ),
            models.Index(
                fields=["category", "-date_time_create"], name="cat_created_idx"
            ),
            models.Index(fields=["category", "brand"]),
            models.Index(fields=["-views"], name="views_idx"),
        ]


# Конкретная комбинация. Например: Футболка + Красная + XL.
# SKU (Stock Keeping Unit) - единица складского учёта
class ProductVariant(SingleMainMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
        related_name="variants",
    )
    # Уникальный артикул
    # Добавить автогенерацию артикула
    sku = models.CharField(
        "Артикул (SKU)", max_length=50, unique=True, editable=False
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(
        "Остаток на складе", validators=[MaxValueValidator(9999)]
    )

    is_active = models.BooleanField("Активен", default=False)
    attribute_values = models.ManyToManyField(
        AttributeValue, verbose_name="Характеристики варианта"
    )

    def generate_unique_sku(self):
        return uuid.uuid4().hex[:9].upper()

    def save(self, *args, **kwargs):
        # Обертываем в транзакцию, чтобы снятие флага и сохранение произошли одновременно
        with transaction.atomic():
            self._handle_main_logic("product", Product)

            # Блок сохранения и генерации SKU, если его нет
            if not self.sku:
                # Если SKU нет, генерируем с защитой от коллизий
                saved = False
                for _ in range(20):
                    self.sku = self.generate_unique_sku()
                    try:
                        with transaction.atomic():
                            super().save(*args, **kwargs)
                            saved = True
                            break
                    except IntegrityError:
                        self.sku = ""

                if not saved:
                    raise RuntimeError(
                        "Не удалось сгенерировать уникальный SKU"
                    )

                return

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.sku})"

    class Meta:
        verbose_name = "Вариант товара (SKU)"
        verbose_name_plural = "Варианты товаров (SKU)"

        indexes = [
            models.Index(fields=["is_active", "price"], name="active_price_idx")
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_main=True),
                name="unique_main_variant_per_product",
            )
        ]


# Отдельная модель изображений
class ProductImage(SingleMainMixin):
    # Сделать возможность на 12 фотографий и 2 видео в будущем
    image = models.ImageField("Изображение", upload_to=r"products/%Y/%m/%d/")

    # Можно не указывать и сделать общим главным фото
    # без вариантов товара саму модель Product
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        verbose_name="Вариант (SKU)",
        related_name="images",
    )

    def clean(self):
        super().clean()

        # Ограничение количества фоток
        if self._state.adding:
            if (
                ProductImage.objects.filter(variant_id=self.variant_id).count()
                >= 12
            ):
                raise ValidationError(
                    {"image": "Максимум 12 изображений на один вариант товара."}
                )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self._handle_main_logic("variant", ProductVariant)

            super().save(*args, **kwargs)

    def __str__(self):
        return f"Фото для {self.variant.sku}"

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ["-is_main", "pk"]

        constraints = [
            models.UniqueConstraint(
                fields=["variant"],
                condition=models.Q(is_main=True),
                name="unique_main_image_per_variant",
            )
        ]
