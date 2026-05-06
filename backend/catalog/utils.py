from math import ceil

from rest_framework.request import Request

from .pagination import FilterValuesPagination


def get_limited_data(
    request: Request,
    qs,
    serializer_class,
    prefix,
    limit=FilterValuesPagination.page_size,
):
    try:
        start = max(
            0,
            ceil(
                (int(request.query_params.get(f"{prefix}_start") or 0)) / limit
            )
            * limit,
        )

        qs_limited = qs[start : start + limit]

        total_count = qs.count()

        previous_offset = max(0, start - limit) if start > 0 else None
        start_offset = start + limit if start + limit < total_count else None

        return {
            "prefix": f"{prefix}_start",
            "next": start_offset,
            "previous": previous_offset,
            "results": serializer_class(
                qs_limited, many=True, context={"request": request}
            ).data,
        }
    except (ValueError, TypeError):
        return {
            "next": None,
            "previous": None,
            "results": serializer_class(
                qs[:limit], many=True, context={"request": request}
            ).data,
        }
