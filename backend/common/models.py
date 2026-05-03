from django.db import models

from .mixins import SlugifiedNameMixin


class SiteConfiguration(models.Model):
    """Модель-одиночка для глобальных настроек сайта"""

    max_discount_percentage = models.DecimalField(
        "Максимальная скидка на сайте",
        max_digits=3,
        decimal_places=2,
        default=0.50,
    )

    def save(self, *args, **kwargs):
        self.pk = 1  # Гарантируем, что запись всегда будет только одна
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Tag(SlugifiedNameMixin):
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        abstract = True
