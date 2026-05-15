from common.phone import normalize_ru_mobile_phone
from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Creates or updates the development superuser from the technical spec."

    def handle(self, *args, **options):
        phone = normalize_ru_mobile_phone("89642297622")
        user, created = CustomUser.objects.get_or_create(phone_number=phone)
        user.set_password("qwerty123456")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Superuser {phone} {action}."))
