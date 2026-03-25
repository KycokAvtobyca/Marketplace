from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
)
from django.db import models
from slugify import slugify


class SlugifiedName(models.Model):
    name = models.CharField(
        "Название",
        unique=True,
        max_length=50,
        validators=[MinLengthValidator(3)],
    )
    slug = models.SlugField(
        "Слаг (для URL)", unique=True, max_length=80, blank=True
    )

    def save(self, *args, **kwargs):
        # автосохранение и изменение
        # if self.pk:
        #     old_obj = self.__class__.objects.get(pk=self.pk)
        #     if old_obj.name != self.name:
        #         self.slug = slugify(self.name)
        # else:
        #     self.slug = slugify(self.name)

        if not self.slug:
            self.slug = slugify(self.name)

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


# --- Базовые справочники ---
class Category(SlugifiedName):
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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"


# ------


# Конкретное значение свойства
# Красный, XL, Кожа
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=50, validators=[MinLengthValidator(2)])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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


# Общая карточка, то что статично
class Product(SlugifiedName):
    description = models.TextField(
        "Описание товара",
        max_length=4000,
        blank=True,
        validators=[MinLengthValidator(10)],
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
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
    date_time_create = models.DateTimeField(
        "Дата создания", auto_now_add=True
    )  # Должно быть в будущем неизменяемым полем
    date_time_update = models.DateTimeField(
        "Дата последнего изменения", auto_now=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Кто последний обновил",
        related_name="updated_products",
    )
    attributes = models.ManyToManyField(
        Attribute, verbose_name="Доступные атрибуты", blank=True
    )
    # image = models.ImageField("Изображение по умолчанию", upload_to=r"products/%Y/%m/%d/", blank=True, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар (карточка)"
        verbose_name_plural = "Товары (карточки)"

        indexes = [
            models.Index(
                fields=["-date_time_create"], name="product_created_idx"
            )
        ]


# Конкретная комбинация. Например: Футболка + Красная + XL.
# SKU (Stock Keeping Unit) - единица складского учёта
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Товар",
        related_name="variants",
    )
    # Уникальный артикул
    sku = models.CharField("Артикул (SKU)", max_length=50, unique=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(
        "Остаток на складе", validators=[MaxValueValidator(9999)]
    )
    is_active = models.BooleanField("Активен", default=False, db_index=True)
    attribute_values = models.ManyToManyField(
        AttributeValue, verbose_name="Характеристики варианта"
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.sku})"

    class Meta:
        verbose_name = "Вариант товара (SKU)"
        verbose_name_plural = "Варианты товаров (SKU)"


# Отдельная модель изображений
class ProductImage(models.Model):
    image = models.ImageField(
        "Изображение", upload_to=r"products/%Y/%m/%d/"
    )  # настроить поле
    is_main = models.BooleanField("Главное фото", default=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Товар",
        related_name="images",
    )

    # Можно не указывать и сделать общим главным фото
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Вариант (SKU)",
        related_name="images",
    )

    # Добавить save метод или constraint для возможности одного пустого variant

    def __str__(self):
        return f"Фото для {self.product.name}"

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(variant__isnull=True),
                name="unique_general_image_per_product",
            ),
            models.UniqueConstraint(
                fields=["variant"],
                condition=models.Q(is_main=True),
                name="unique_main_image",
            ),
        ]
