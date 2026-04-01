from django.db import models
from django.db.models import F, OuterRef, Subquery
from django.db.models.functions import Coalesce

# class Priority(models.IntegerChoices):
#     NULL = 0, "Не задан"
#     GLOBAL = 1, "На все (Глобальная)"
#     CATEGORY = 2, "На категорию"
#     BRAND = 3, "На бренд"
#     TAG = 4, "На тег (подборку)"
#     PRODUCT = 5, "На товар"
#     VARIANT = 6, "На вариацию товара (SKU)"
#     SEGMENT = 7, "На сегмент пользователей"
#     USER = 8, "На конкретного пользователя"


class ProductVariantQuerySet(models.QuerySet):
    def with_prices(self, user=None):
        """
        Аннотирует каждый вариант товара актуальной ценой
        с учетом общих и персональных скидок.
        """
        from marketing.models import Discount

        # Подзапрос: ищем самую приоритетную активную скидку
        # Базовые фильтры (доступны всем)
        discount_filter = models.Q(
            models.Q(product_variant_id=OuterRef("pk"))
            | models.Q(product_id=OuterRef("product_id"))
            | models.Q(tag_id=OuterRef("tag_id"))
            | models.Q(brand_id=OuterRef("brand_id"))
            | models.Q(category_id=OuterRef("category_id"))
            | models.Q(is_global=True)
        )

        # Расширяем фильтр, если передан авторизованный пользователь
        if user and user.is_authenticated:
            discount_filter |= models.Q(user_id=user.id)

            segment_ids = user.segments.values_list("id", flat=True)

            if segment_ids:
                discount_filter |= models.Q(segment_id__in=segment_ids)

        active_discounts = (
            Discount.objects.active()
            .filter(discount_filter)
            .order_by("-priority")
        )

        return self.annotate(
            discount_pct=Coalesce(
                Subquery(active_discounts.values("discount_percentage")[:1]),
                models.Value(0, output_field=models.DecimalField()),
            ),
            discounted_price=F("price") * (models.Value(1) - F("discount_pct")),
        )
