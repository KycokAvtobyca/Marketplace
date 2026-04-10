import os
import uuid

from common.models import (
    DateTimeCreateMixin,
    DateTimeUpdateMixin,
    SingleMainMixin,
    SlugifiedNameMixin,
    Tag,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
)
from django.db import IntegrityError, models, transaction
from slugify import slugify

from .managers import ProductVariantQuerySet


# Сделать ограничение на макс 20 тегов в формах и api
class ProductTag(Tag):
    def __str__(self):
        return f"Тег продукта. {self.name}"


# --- Базовые справочники ---
class Category(SlugifiedNameMixin):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


def brand_image_path(instance, filename):
    """
    Генерирует путь: media/brands/slug-name/filename
    """

    folder = slugify(instance.name)

    if not folder:
        folder = f"brand_{instance.pk or 'new'}"

    return os.path.join("brands", folder, filename)


class Brand(models.Model):
    name = models.CharField(
        "Бренд", max_length=50, validators=[MinLengthValidator(2)], unique=True
    )
    description = models.TextField(
        "Описание бренда", max_length=5000, blank=True
    )
    image = models.ImageField("Изображение", upload_to=brand_image_path)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


# Категория свойства, то что вообще бывает.
# Например: Цвет, Размер
class Attribute(models.Model):
    name = models.CharField(
        "Название атрибута",
        unique=True,
        max_length=99,
        validators=[MinLengthValidator(2)],
    )

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"

    def __str__(self):
        return self.name


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

    class Meta:
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"

        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"], name="unique_attribute_value"
            )
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


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
    tags = models.ManyToManyField(
        ProductTag, verbose_name="Теги продукта", blank=True
    )

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

    def __str__(self):
        return f"{self.name} ({self.pk})"


# Конкретная комбинация. Например: Футболка + Красная + XL.
# SKU (Stock Keeping Unit) - единица складского учёта
class ProductVariant(SingleMainMixin):
    objects = ProductVariantQuerySet.as_manager()

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

    def __str__(self):
        return f"{self.product.name} ({self.sku})"

    @property
    def final_price(self):
        """
        Удобный доступ к цене.
        Если мы вызвали .with_prices(user), берем из БД.
        Если нет - возвращаем базовую цену.
        """
        return getattr(self, "discounted_price", self.price)

    @property
    def has_discount(self):
        """Проверка для фронтенда: рисовать ли зачеркнутую цену."""
        return self.final_price < self.price

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


# Отдельная модель изображений
class ProductImage(SingleMainMixin):
    # Сделать возможность 2 видео в будущем
    image = models.ImageField("Изображение", upload_to=r"products/%Y/%m/%d/")

    # Можно не указывать и сделать общим главным фото
    # без вариантов товара саму модель Product
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        verbose_name="Вариант (SKU)",
        related_name="images",
    )

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

    def __str__(self):
        return f"Фото для {self.variant.sku}"

    def clean(self):
        super().clean()

        # Ограничение количества фоток
        if self._state.adding and self.variant_id:
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
