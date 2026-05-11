"""
Утилиты для Django админки.
Содержит базовый класс админ-интерфейса и простые фильтры.
"""

from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.html import format_html, mark_safe


class BaseModelAdmin(admin.ModelAdmin):
    """Базовый класс для админ-интерфейса"""

    date_hierarchy = None
    list_per_page = 25
    list_max_show_all = 100


class PriceListFilter(admin.SimpleListFilter):
    """Фильтр по диапазону цен"""

    title = "Диапазон цены"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return (
            ("0-1000", "0 - 1 000 руб."),
            ("1000-5000", "1 000 - 5 000 руб."),
            ("5000-10000", "5 000 - 10 000 руб."),
            ("10000-", "10 000 руб. и выше"),
        )

    def queryset(self, request, queryset):
        if self.value() == "0-1000":
            return queryset.filter(variants__price__lt=1000)
        elif self.value() == "1000-5000":
            return queryset.filter(
                variants__price__gte=1000, variants__price__lt=5000
            )
        elif self.value() == "5000-10000":
            return queryset.filter(
                variants__price__gte=5000, variants__price__lt=10000
            )
        elif self.value() == "10000-":
            return queryset.filter(variants__price__gte=10000)
        return queryset


class StockListFilter(admin.SimpleListFilter):
    """Фильтр по наличию товара"""

    title = "Статус остатка"
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return (
            ("in_stock", "В наличии"),
            ("low_stock", "Мало товара"),
            ("no_stock", "Нет в наличии"),
        )

    def queryset(self, request, queryset):
        if self.value() == "in_stock":
            return queryset.filter(stock__gte=10)
        elif self.value() == "low_stock":
            return queryset.filter(stock__gte=1, stock__lt=10)
        elif self.value() == "no_stock":
            return queryset.filter(stock=0)
        return queryset


class CreatedDateListFilter(admin.SimpleListFilter):
    """Фильтр по дате создания"""

    title = "Дата создания"
    parameter_name = "created_date"

    def lookups(self, request, model_admin):
        return (
            ("today", "Сегодня"),
            ("week", "На этой неделе"),
            ("month", "В этом месяце"),
            ("old", "Давно"),
        )

    def queryset(self, request, queryset):
        today = datetime.now().date()
        if self.value() == "today":
            return queryset.filter(date_time_create__date=today)
        elif self.value() == "week":
            week_start = today - timedelta(days=today.weekday())
            return queryset.filter(date_time_create__date__gte=week_start)
        elif self.value() == "month":
            month_start = today.replace(day=1)
            return queryset.filter(date_time_create__date__gte=month_start)
        elif self.value() == "old":
            month_ago = today - timedelta(days=30)
            return queryset.filter(date_time_create__date__lt=month_ago)
        return queryset


class ActiveListFilter(admin.SimpleListFilter):
    """Фильтр по активности"""

    title = "Статус активности"
    parameter_name = "activity_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Активно"),
            ("inactive", "Неактивно"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False)
        return queryset


# Простые форматирующие функции


def image_thumbnail(image, width=50, height=50):
    """Возвращает миниатюру изображения"""
    if image:
        return format_html(
            '<img src="{url}" width="{width}" height="{height}" '
            'style="border-radius: 4px; object-fit: cover; border: 1px solid #e5e7eb;"/>',
            url=image.url,
            width=width,
            height=height,
        )
    return mark_safe(
        '<span style="color: #999; font-style: italic;">Нет изображения</span>'
    )


def image_preview(image, width=300):
    """Возвращает полный размер изображения для предпросмотра"""
    if image:
        return format_html(
            '<img src="{url}" style="max-width: {width}px; height: auto; border-radius: 4px; '
            'border: 1px solid #e5e7eb;"/>',
            url=image.url,
            width=width,
        )
    return mark_safe(
        '<span style="color: #999; font-style: italic;">Нет изображения</span>'
    )

    extra = 0
