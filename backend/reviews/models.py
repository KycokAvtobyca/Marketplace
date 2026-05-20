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
from django.db import connection, models, transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
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

        # Разрешаем отзывы для всех статусов, при которых товар уже доставлен
        exists = OrderItem.objects.filter(
            order__user_id=self.user_id,
            product_variant_id=self.product_variant_id,
            order__status=Order.Status.PAID,
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


class ReviewVote(DateTimeCreateMixin, DateTimeUpdateMixin):
    class Value(models.TextChoices):
        USEFUL = "USEFUL", "Полезно"
        UNUSEFUL = "UNUSEFUL", "Неполезно"

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name="Отзыв",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_votes",
        verbose_name="Пользователь",
    )
    value = models.CharField("Голос", max_length=10, choices=Value.choices)

    class Meta:
        verbose_name = "Голос за отзыв"
        verbose_name_plural = "Голоса за отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["review", "user"],
                name="unique_review_vote_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user_id}: {self.value} for review {self.review_id}"


class ProductQuestion(DateTimeCreateMixin, DateTimeUpdateMixin):
    class ModerationStatus(models.TextChoices):
        PENDING = "PENDING", "На модерации"
        APPROVED = "APPROVED", "Одобрен"
        REJECTED = "REJECTED", "Отклонен"

    class AnswerStatus(models.TextChoices):
        NONE = "NONE", "Нет ответа"
        PENDING = "PENDING", "Ответ на модерации"
        APPROVED = "APPROVED", "Ответ одобрен"
        REJECTED = "REJECTED", "Ответ отклонен"

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Товар",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="product_questions",
        verbose_name="Автор вопроса",
    )
    text = models.TextField(
        "Вопрос",
        max_length=2000,
        validators=[MinLengthValidator(5)],
    )
    answer = models.TextField("Ответ продавца", max_length=2000, blank=True)
    pending_answer = models.TextField(
        "Ответ продавца на модерации",
        max_length=2000,
        blank=True,
    )
    question_status = models.CharField(
        "Статус модерации вопроса",
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        db_index=True,
    )
    answer_status = models.CharField(
        "Статус модерации ответа",
        max_length=20,
        choices=AnswerStatus.choices,
        default=AnswerStatus.NONE,
        db_index=True,
    )
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answered_product_questions",
        verbose_name="Ответил",
    )
    answered_at = models.DateTimeField("Дата ответа", null=True, blank=True)
    is_public = models.BooleanField("Показывать на сайте", default=False)

    class Meta:
        verbose_name = "Вопрос о товаре"
        verbose_name_plural = "Вопросы о товарах"
        ordering = ["-date_time_create", "-id"]
        indexes = [
            models.Index(fields=["product", "-date_time_create"]),
            models.Index(fields=["is_public", "-date_time_create"]),
        ]

    def set_answer(self, user, answer):
        self.pending_answer = answer.strip()
        self.answered_by = user
        self.answered_at = timezone.now()
        self.answer_status = self.AnswerStatus.PENDING
        self.save(
            update_fields=[
                "pending_answer",
                "answer_status",
                "answered_by",
                "answered_at",
                "date_time_update",
            ]
        )

    def approve_answer(self):
        if self.pending_answer:
            self.answer = self.pending_answer
            self.answer_status = self.AnswerStatus.APPROVED

    def save(self, *args, **kwargs):
        self.is_public = self.question_status == self.ModerationStatus.APPROVED
        if self.answer_status == self.AnswerStatus.APPROVED and self.pending_answer:
            self.answer = self.pending_answer
        if not self.pending_answer and self.answer_status != self.AnswerStatus.NONE:
            self.answer_status = self.AnswerStatus.NONE
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            update_fields.add("is_public")
            update_fields.add("answer_status")
            if self.answer_status == self.AnswerStatus.APPROVED and self.pending_answer:
                update_fields.add("answer")
            kwargs["update_fields"] = list(update_fields)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Вопрос #{self.pk} к товару {self.product_id}"


@receiver(pre_delete, sender=ProductQuestion)
def delete_legacy_product_question_moderation_rows(sender, instance, **kwargs):
    legacy_tables = (
        "reviews_answermoderationrequest",
        "reviews_questionmoderationrequest",
    )
    table_names = set(connection.introspection.table_names())
    with connection.cursor() as cursor:
        for table in legacy_tables:
            if table in table_names:
                quoted_table = connection.ops.quote_name(table)
                cursor.execute(
                    f"DELETE FROM {quoted_table} WHERE question_id = %s",
                    [instance.pk],
                )


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


class Report(DateTimeCreateMixin, DateTimeUpdateMixin):
    class TargetType(models.TextChoices):
        REVIEW = "REVIEW", "Отзыв"
        PRODUCT = "PRODUCT", "Товар"

    class Reason(models.TextChoices):
        SPAM = "SPAM", "Спам или реклама"
        OFFENSIVE = "OFFENSIVE", "Оскорбления или недопустимый контент"
        FAKE = "FAKE", "Поддельный/фейковый отзыв или товар"
        WRONG_PRODUCT = "WRONG_PRODUCT", "Товар не соответствует описанию"
        OTHER = "OTHER", "Другое"

    class Status(models.TextChoices):
        PENDING = "PENDING", "На рассмотрении"
        RESOLVED = "RESOLVED", "Решена"
        REJECTED = "REJECTED", "Отклонена"

    target_type = models.CharField(
        "Тип объекта", max_length=20, choices=TargetType.choices
    )
    target_id = models.PositiveIntegerField("ID объекта")
    reason = models.CharField("Причина", max_length=30, choices=Reason.choices)
    description = models.TextField(
        "Описание",
        max_length=2000,
        blank=True,
        validators=[MinLengthValidator(5)],
    )
    status = models.CharField(
        "Статус", max_length=15, choices=Status.choices, default=Status.PENDING
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports",
        verbose_name="Автор жалобы",
    )

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"
        ordering = ["-date_time_create"]
        indexes = [
            models.Index(fields=["target_type", "target_id", "status"]),
            models.Index(fields=["status", "-date_time_create"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target_type", "target_id"],
                name="unique_user_report_per_target",
            )
        ]

    def __str__(self):
        return f"{self.get_target_type_display()} #{self.target_id}"


class ComplaintBase(DateTimeCreateMixin, DateTimeUpdateMixin):
    class Reason(models.TextChoices):
        SPAM = "SPAM", "Спам"
        OFFENSIVE = "OFFENSIVE", "Оскорбительный контент"
        FAKE = "FAKE", "Недостоверная информация"
        PROHIBITED = "PROHIBITED", "Запрещенный товар или контент"
        OTHER = "OTHER", "Другое"

    class Status(models.TextChoices):
        NEW = "NEW", "Новая"
        IN_REVIEW = "IN_REVIEW", "На проверке"
        RESOLVED = "RESOLVED", "Решена"
        REJECTED = "REJECTED", "Отклонена"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_complaints",
        verbose_name="Автор жалобы",
    )
    reason = models.CharField("Причина", max_length=20, choices=Reason.choices)
    text = models.TextField("Комментарий", max_length=2000, blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )

    class Meta:
        abstract = True
        ordering = ["-date_time_create", "-id"]


class ReviewComplaint(ComplaintBase):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="complaints",
        verbose_name="Отзыв",
    )

    class Meta(ComplaintBase.Meta):
        verbose_name = "Жалоба на отзыв"
        verbose_name_plural = "Жалобы на отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["review", "user"],
                name="unique_review_complaint_per_user",
            )
        ]

    def __str__(self):
        return f"Жалоба на отзыв #{self.review_id}"


class ProductComplaint(ComplaintBase):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="complaints",
        verbose_name="Товар",
    )

    class Meta(ComplaintBase.Meta):
        verbose_name = "Жалоба на товар"
        verbose_name_plural = "Жалобы на товары"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_product_complaint_per_user",
            )
        ]

    def __str__(self):
        return f"Жалоба на товар #{self.product_id}"
