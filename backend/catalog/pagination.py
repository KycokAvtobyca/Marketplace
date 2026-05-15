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


class ProductCatalogPagination(DefaultCursorPagination):
    sort_ordering = {
        "price_asc": ("-has_stock", "api_price", "id"),
        "price_desc": ("-has_stock", "-api_price", "-id"),
        "new": ("-has_stock", "-date_time_create", "-id"),
        "popular": ("-has_stock", "-api_rating", "-views", "-id"),
        "views_desc": ("-has_stock", "-views", "-id"),
        "rating_desc": ("-has_stock", "-api_rating", "-id"),
    }

    def get_ordering(self, request, queryset, view):
        sort = request.query_params.get("sort", "new")
        return self.sort_ordering.get(sort, self.sort_ordering["new"])


class DefaultOrderPagination(CursorPagination):
    """Pagination класс для заказов."""
    page_size = api_settings.PAGE_SIZE
    cursor_query_param = "cursor"
    ordering = "-date_time_create"  # Новые заказы в начале
    template = None
