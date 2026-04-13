from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled) and response is not None:
        view = context.get("view")

        if view:
            throttle = view.get_throttles()[0]

            response.data["detail"] = {}

            if hasattr(throttle, "message"):
                response.data["detail"]["message"] = throttle.message

            if hasattr(exc, "wait"):
                response.data["detail"]["seconds_left"] = exc.wait

    return response
