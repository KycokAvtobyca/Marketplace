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
