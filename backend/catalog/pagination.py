from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings


def extract_token(url):
    if not url:
        return None
    # Находим где начинается ?cursor= и берем всё что после =
    if "cursor=" in url:
        return url.split("cursor=")[-1].split("&")[0]
    return None


class FilterValuesPagination(CursorPagination):
    page_size = 10
    cursor_query_param = "cursor"
    ordering = "-id"
    template = None

    def get_paginated_response(self, data):
        return Response(
            {
                "next": extract_token(self.get_next_link()),
                "previous": extract_token(self.get_previous_link()),
                "results": data,
            }
        )


class DefaultCursorPagination(CursorPagination):
    page_size = api_settings.PAGE_SIZE
    cursor_query_param = "cursor"
    ordering = ("-date_time_create", "-id")
    template = None


class DefaultOrderPagination(CursorPagination):
    """Pagination класс для заказов."""
    page_size = api_settings.PAGE_SIZE
    cursor_query_param = "cursor"
    ordering = "-date_time_create"  # Новые заказы в начале
    template = None
