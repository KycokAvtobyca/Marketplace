from django.utils.translation import gettext_lazy as _
from rest_framework.throttling import SimpleRateThrottle


class SMSRateThrottle(SimpleRateThrottle):
    scope = "sms"
    message = _(
        "Слишком много запросов на получение СМС-кода. Пожалуйста, подождите минуту."
    )

    def get_cache_key(self, request, view):
        return self.get_ident(request)
