from catalog.models import ProductVariant
from common.models import DateTimeCreateMixin, DateTimeUpdateMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models, transaction


class Review(DateTimeCreateMixin, DateTimeUpdateMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор",
        related_name="reviews",
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        verbose_name="Вариант товара",
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField("Текст отзыва", max_length=4000)

    def __str__(self):
        if self.user:
            return f"Оценка {self.rating} от отзыва пользователя {self.user.phone_number}"
        return f"Оценка {self.rating} от отзыва удаленного пользователя"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

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


class ReviewImage(models.Model):
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
            if type(self).objects.filter(review_id=self.review_id).count() >= 9:
                raise ValidationError(
                    {
                        "image": "К одному отзыву можно прикрепить не более 8 изображений."
                    }
                )

    # Защита от гонки
    def save(self, *args, **kwargs):
        if self._state.adding and self.review_id:
            with transaction.atomic():
                # Напрямую обращаемся к Review,
                # чтобы не тянуть тяжелый SQL запрос
                # Запираем дверь (Mutex)
                Review.objects.select_for_update().get(pk=self.review_id)

                # После Mutex делаем синхронизацию с бд
                # только если объект уже существует в базе

                if not self._state.adding:
                    self.refresh_from_db()

                current_count = (
                    type(self).objects.filter(review_id=self.review_id).count()
                )

                if current_count >= 9:
                    raise ValidationError(
                        "К одному отзыву можно прикрепить не более 8 изображений."
                    )

                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Изображение отзыва"
        verbose_name_plural = "Изображения отзывов"
