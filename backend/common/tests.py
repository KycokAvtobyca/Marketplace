from django.test import SimpleTestCase

from .phone import PhoneValidationError, normalize_ru_mobile_phone


class RuMobilePhoneTests(SimpleTestCase):
    def test_normalizes_allowed_mobile_formats(self):
        self.assertEqual(normalize_ru_mobile_phone("89642297622"), "+79642297622")
        self.assertEqual(normalize_ru_mobile_phone("+79642297622"), "+79642297622")
        self.assertEqual(normalize_ru_mobile_phone("9642297622"), "+79642297622")

    def test_rejects_non_mobile_or_short_numbers(self):
        invalid_values = ["", "83952297622", "+73952297622", "123", "+9969642297622"]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(PhoneValidationError):
                    normalize_ru_mobile_phone(value)
