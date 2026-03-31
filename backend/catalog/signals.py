from django.db.models.signals import post_delete
from django.dispatch import receiver

from catalog.models import ProductImage, ProductVariant


def reassign_main_object_on_delete_logic(sender, instance, parent_field_name):
    """
    Сигнал ловит удаление объекта из модели.
    Если удалили главный объект, передаем статус 'is_main' любому оставшемуся.
    """
    # В момент post_delete записи в БД уже нет,
    # но сам python-объект instance всё еще хранит свои данные в памяти
    if instance.is_main:
        parent_id = getattr(instance, f"{parent_field_name}_id")

        if not parent_id:
            raise AttributeError(
                "ID Родительского объекта не был найден"
                "(reassign_main_object_on_delete_logic {parent_field_name}_id)."
            )

        # Ищем любой оставшийся вариант для этого же товара
        next_variant = sender.objects.filter(
            **{f"{parent_field_name}_id": parent_id}
        ).first()

        if next_variant:
            # Назначаем его главным
            next_variant.is_main = True
            # save(update_fields=...) нужен для оптимизации:
            # мы обновляем только одно поле, а не перезаписываем всю строку
            next_variant.save(update_fields=["is_main"])


@receiver(post_delete, sender=ProductVariant)
def reassign_main_variant_on_delete(sender, instance, **kwargs):
    reassign_main_object_on_delete_logic(sender, instance, "product")


@receiver(post_delete, sender=ProductImage)
def reassign_main_image_on_delete(sender, instance, **kwargs):
    reassign_main_object_on_delete_logic(sender, instance, "variant")
