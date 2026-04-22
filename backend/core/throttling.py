from rest_framework.throttling import SimpleRateThrottle


class BaseThrottle(SimpleRateThrottle):
    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)

        if not allowed:
            request.throttle_instance = self

        return allowed
