from core.throttling import BaseThrottle
from django.utils.translation import gettext_lazy as _


class AuthTokenIPThrottle(BaseThrottle):
    scope = "auth_token_ip"
    message = _("Слишком много попыток. Попробуйте позже.")

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class AuthTokenByPhone(BaseThrottle):
    scope = "auth_token_phone"
    message = _(
        "Слишком частые попытки входа для этого номера. Попробуйте позже."
    )

    def get_cache_key(self, request, view):
        phone = request.data.get("phone_number")

        if not phone:
            return None

        return self.cache_format % {"scope": self.scope, "ident": phone}


class SMSIpThrottle(BaseThrottle):
    scope = "sms_ip"
    message = _(
        "Слишком много запросов на получение СМС-кода. Пожалуйста, подождите минуту."
    )

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}


class SMSByPhoneThrottle(BaseThrottle):
    scope = "sms_phone"
    message = _(
        "Слишком много запросов на получение СМС-кода по данному номеру телефона. Пожалуйста, попробуйте позже."
    )

    def get_cache_key(self, request, view):
        phone = request.data.get("phone_number")

        if not phone:
            return None

        return self.cache_format % {"scope": self.scope, "ident": phone}
