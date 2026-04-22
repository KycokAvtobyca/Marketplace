from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled) and response is not None:
        request = context.get("request")
        throttle = getattr(request, "throttle_instance", None)

        response.data = {
            "detail": {
                "message": getattr(throttle, "message", str(exc.detail)),
                "seconds_left": int(exc.wait) if exc.wait else None,
            }
        }

    return response
