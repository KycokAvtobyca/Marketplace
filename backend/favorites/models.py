from common.models import DateTimeCreateMixin, DateTimeUpdateMixin
from django.conf import settings
from django.db import models
from django.utils import timezone


class Favorite(DateTimeCreateMixin, DateTimeUpdateMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Пользователь",
    )
    items = models.ManyToManyField(
        "catalog.ProductVariant",
        through="FavoriteItem",
        related_name="favorites",
        verbose_name="Элементы избранных",
    )

    def __str__(self):
        return f"Избранное {self.user.phone_number} ({self.pk})"

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class FavoriteItem(DateTimeCreateMixin):
    favorite = models.ForeignKey(
        Favorite,
        on_delete=models.CASCADE,
        related_name="favorite_items",
        verbose_name="Избранное",
    )
    product_variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        related_name="favorite_lines",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Принудительно обновляем дату изменения избранного
        Favorite.objects.filter(pk=self.favorite_id).update(
            date_time_update=timezone.now()
        )

    def delete(self, *args, **kwargs):
        # Сохраняем ID перед удалением
        favorite_id = self.favorite_id

        super().delete(*args, **kwargs)

        # Обновляем дату, так как состав избранного изменился
        if favorite_id:
            Favorite.objects.filter(pk=favorite_id).update(
                date_time_update=timezone.now()
            )

    def __str__(self):
        return str(self.product_variant)

    class Meta:
        verbose_name = "Элемент избранного"
        verbose_name_plural = "Элементы избранных товаров"

        constraints = [
            models.UniqueConstraint(
                fields=["favorite", "product_variant"],
                name="unique_favorite_variant",
            )
        ]
