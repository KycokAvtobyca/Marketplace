from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models, transaction
from slugify import slugify


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


class SlugifiedNameMixin(models.Model):
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
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class DateTimeCreateMixin(models.Model):
    date_time_create = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        abstract = True


class DateTimeUpdateMixin(models.Model):
    date_time_update = models.DateTimeField(
        "Дата последнего изменения", auto_now=True
    )

    class Meta:
        abstract = True


class SingleMainMixin(models.Model):
    """
    Миксин для моделей, где должен быть строго один главный элемент.
    Запрещает снимать флаг is_main вручную.
    """

    is_main = models.BooleanField("Главный", default=False)

    @transaction.atomic
    def _handle_main_logic(self, parent_field_name, parent_mode):
        """
        Инкапсулирует логику выбора единственного главного элемента среди детей одного родителя.
        """

        parent_id = getattr(self, f"{parent_field_name}_id")

        if not parent_id:
            raise ValidationError(
                "ID Родительского объекта не был найден (_handle_main_logic {parent_field_name}_id)."
            )

        if not getattr(parent_mode, "objects"):
            raise ValidationError(
                "Передана неверная модель (_handle_main_logic)"
            )

        # Запираем дверь (Mutex)
        parent_mode.objects.select_for_update().get(pk=parent_id)

        # После Mutex делаем синхронизацию с бд
        # только если объект уже существует в базе
        if not self._state.adding:
            self.refresh_from_db()

        if self.is_main:
            # Если текущий вариант становится главным, жестко снимаем флаг с остальных
            type(self).objects.filter(
                **{f"{parent_field_name}_id": parent_id, "is_main": True}
            ).exclude(pk=self.pk).update(is_main=False)
        elif (
            self._state.adding
            and not type(self)
            .objects.filter(**{f"{parent_field_name}_id": parent_id})
            .exists()
        ):
            # Если это самый первый вариант у товара, делаем его главным принудительно
            self.is_main = True

        # save или update нужно реализовать

    def validate_constraints(self, exclude=None):
        if exclude is None:
            exclude = set()

        exclude.add("is_main")

        return super().validate_constraints(exclude)

    def clean(self):
        super().clean()

        if self.pk and not self.is_main:
            was_main = (
                type(self).objects.filter(pk=self.pk, is_main=True).exists()
            )

            if was_main:
                model_name = self._meta.verbose_name.lower()

                raise ValidationError(
                    {
                        "is_main": "Нельзя просто снять этот флаг. "
                        f"Чтобы сменить главный {model_name}, установите "
                        "галочку 'Главный' у другого объекта"
                    }
                )

    class Meta:
        abstract = True


class Tag(SlugifiedNameMixin):
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        abstract = True
