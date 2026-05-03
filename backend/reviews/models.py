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
from django.db import models, transaction
from django.utils.functional import cached_property


class Review(DateTimeCreateMixin, DateTimeUpdateMixin):
    class Status(models.TextChoices):
        PENDING = "PENDING", "На проверке"
        APPROVED = "APPROVED", "Одобрен"
        REJECTED = "REJECTED", "Отклонен"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор",
        related_name="reviews",
    )
    product_variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        verbose_name="Вариант товара",
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField(
        "Текст отзыва", max_length=4000, validators=[MinLengthValidator(10)]
    )
    status = models.CharField(
        "Статус модерации",
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    is_verified_purchase = models.BooleanField(
        "Купленный товар",
        default=False,
        help_text="Был ли товар действительно куплен этим пользователем",
    )

    # Социальная составляющая
    useful_count = models.PositiveIntegerField("Полезно", default=0)
    unuseful_count = models.PositiveIntegerField("Бесполезно", default=0)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

        ordering = ["-date_time_create"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product_variant"],
                name="unique_user_product_variant",
            )
        ]

        indexes = [
            models.Index(
                fields=["product_variant", "-date_time_create"],
                name="review_variant_date_idx",
            ),
            models.Index(
                fields=["product_variant", "rating"],
                name="review_product_rating_idx",
            ),
            models.Index(
                fields=["-date_time_create"], name="review_created_idx"
            ),
        ]

    def __str__(self):
        author = self.user_id if self.user_id else "удаленного пользователя"
        return f"Оценка {self.rating} от {author}"

    @cached_property
    def can_add_review(self):
        """Проверяет факт покупки товара пользователем"""
        from orders.models import Order, OrderItem

        if not self.user_id or not self.product_variant_id:
            return False

        exists = OrderItem.objects.filter(
            order__user_id=self.user_id,
            product_variant_id=self.product_variant_id,
            order__status=Order.Status.COMPLETED,
        ).exists()

        return exists

    def validate_purchase(self):
        """Метод для валидации покупки"""

        if not self.can_add_review:
            raise ValidationError(
                {
                    "product_variant": "Нельзя оставить отзыв о товаре, который вы не покупали."
                }
            )

    # Ответ от магазина
    # В будущем будем реализована модель ReviewMessage
    # seller_reply = models.TextField("Ответ продавца", max_length=2000, blank=True)
    # admin_reply = models.TextField("Ответ администрации", max_length=2000, blank=True)
    # reply_created_at = models.DateTimeField("Дата ответа", null=True, blank=True)

    def clean(self):
        super().clean()

        if self._state.adding:
            self.validate_purchase()
            self.is_verified_purchase = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.validate_purchase()

        super().save(*args, **kwargs)


class ReviewImage(models.Model):
    MAX_IMAGES_PER_REVIEW = 8

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name="Отзыв",
        related_name="review_images",
    )
    image = models.ImageField("Изображение", upload_to=r"reviews/%Y/%m/%d/")

    def __str__(self):
        return f"Изображение отзыва {self.review_id}"

    def clean(self):
        if self._state.adding and self.review_id:
            if (
                type(self).objects.filter(review_id=self.review_id).count()
                >= self.MAX_IMAGES_PER_REVIEW
            ):
                raise ValidationError(
                    {
                        "image": f"К одному отзыву можно прикрепить не более {self.MAX_IMAGES_PER_REVIEW} изображений."
                    }
                )

    # Защита от гонки
    def save(self, *args, **kwargs):
        if self._state.adding and self.review_id:
            with transaction.atomic():
                # Напрямую обращаемся к Review, чтобы повесить Mutex.
                # Оптимизация: .values('pk') не тянет тяжелые текстовые поля в память.
                Review.objects.select_for_update().values("pk").get(
                    pk=self.review_id
                )

                current_count = (
                    type(self).objects.filter(review_id=self.review_id).count()
                )

                if current_count >= self.MAX_IMAGES_PER_REVIEW:
                    raise ValidationError(
                        {
                            "image": f"К одному отзыву можно прикрепить не более {self.MAX_IMAGES_PER_REVIEW} изображений."
                        }
                    )

                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Изображение отзыва"
        verbose_name_plural = "Изображения отзывов"
