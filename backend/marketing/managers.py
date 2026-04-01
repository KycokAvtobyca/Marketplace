from django.db import models
from django.utils import timezone


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
