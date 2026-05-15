import re

from django.core.exceptions import ValidationError


PHONE_ERROR_MESSAGE = (
    "Введите российский мобильный номер в формате +7XXXXXXXXXX, "
    "8XXXXXXXXXX или 9XXXXXXXXX."
)


class PhoneValidationError(ValueError):
    pass


def normalize_ru_mobile_phone(value: object) -> str:
    """Normalize RU mobile phones to +79XXXXXXXXX."""
    raw = str(value or "").strip()
    digits = re.sub(r"\D", "", raw)

    if not digits:
        raise PhoneValidationError(PHONE_ERROR_MESSAGE)

    if raw.startswith("+"):
        if len(digits) == 11 and digits.startswith("7"):
            normalized = digits
        else:
            raise PhoneValidationError(PHONE_ERROR_MESSAGE)
    elif len(digits) == 11 and digits.startswith("8"):
        normalized = f"7{digits[1:]}"
    elif len(digits) == 11 and digits.startswith("7"):
        normalized = digits
    elif len(digits) == 10 and digits.startswith("9"):
        normalized = f"7{digits}"
    else:
        raise PhoneValidationError(PHONE_ERROR_MESSAGE)

    if len(normalized) != 11 or not normalized.startswith("79"):
        raise PhoneValidationError(PHONE_ERROR_MESSAGE)

    return f"+{normalized}"


def validate_ru_mobile_phone(value: object) -> str:
    try:
        return normalize_ru_mobile_phone(value)
    except PhoneValidationError as exc:
        raise ValidationError(str(exc)) from exc
