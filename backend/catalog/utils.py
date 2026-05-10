from django.db.models import Model
from rest_framework.request import Request

from catalog.models import Category

from .pagination import FilterValuesPagination


def get_limited_data(
    request: Request,
    qs,
    serializer_class,
    prefix,
    name,
    context=None,
    prepare_results=None,
    limit=FilterValuesPagination.page_size,
):
    try:
        start_param = request.query_params.get(f"{prefix}_start") or 0
        start = max(0, int(start_param))

        # 1. Режем QuerySet на уровне БД.
        # До этого момента запросов к базе НЕТ.
        qs_limited = list(qs[start : start + limit + 1])

        has_next = len(qs_limited) > limit
        results = qs_limited[:limit]

        previous = max(0, start - limit) if start > 0 else None

        # Если страница пустая, но мы не на старте - ищем последнюю страницу
        if not qs_limited and start > 0:
            total_count = qs.count()
            previous = max(0, ((total_count - 1) // limit) * limit)

        full_context = {"request": request}
        if context:
            full_context.update(context)

        # Если передан префетч, он сработает только на 20 объектах results
        if prepare_results and callable(prepare_results):
            results, full_context = prepare_results(results, full_context)

        return {
            "name": name,
            "prefix": f"{prefix}_start",
            "next": start + limit if has_next else None,
            "previous": previous,
            "results": serializer_class(
                results, many=True, context=full_context
            ).data,
        }
    except (ValueError, TypeError):
        # Fallback для кривых параметров
        return {
            "name": name,
            "prefix": f"{prefix}_start",
            "next": None,
            "previous": None,
            "results": serializer_class(
                qs[:limit], many=True, context={"request": request}
            ).data,
        }


def prefetch_tree_data(instances, context, depth=3, relation_path="category"):
    """
    Оптимизирует загрузку деревьев категорий.
    :param instances: Список объектов (Page или QuerySet), для которых нужны деревья.
    :param context: Словарь контекста сериализатора.
    :param relation_path: Путь до категории (например, 'category' или 'product__category').
                          Если сами объекты и есть категории, передай "".
    """

    if not instances:
        return context

    # Если это action list и глубина не указана или 0,
    # нам не нужны деревья, сериализатор просто вернет пустые children
    if not depth:
        if context.get("depth", 0):
            depth = context.get("depth", 0)

        if depth == "0":
            print("depth = 0. Возврат")
            return context

    # Собираем все ID категорий из объектов
    category_ids = set()
    for obj in instances:
        # Динамически получаем категорию (поддерживает вложенность типа 'sub_model__category')
        cat = obj

        for attr in relation_path.split("__"):
            if attr:
                cat = getattr(cat, attr, None)

        if cat and isinstance(cat, Model):
            category_ids.add(cat.id)
        elif isinstance(cat, int):  # Если это ID
            category_ids.add(cat)

    # Находим tree_id этих категорий
    if category_ids:
        print("Подгружаем деревья категорий для оптимизации...")
        # Пытаемся собрать tree_id прямо из объектов в памяти
        tree_ids_from_memory = set()
        for obj in instances:
            # Если это категория или category.tree_id
            t_id = getattr(obj, "tree_id", None) or getattr(
                obj.category, "tree_id", None
            )
            if t_id is not None:
                tree_ids_from_memory.add(t_id)

        # Если в памяти tree_id или category.tree_id нет,
        # тогда и только тогда делаем запрос к бд
        if not tree_ids_from_memory:
            # Превращаем QuerySet в список, чтобы избежать подзапросов
            tree_ids_list = list(
                Category.objects.filter(id__in=category_ids)
                .values_list("tree_id", flat=True)
                .distinct()
            )
        else:
            tree_ids_list = list(tree_ids_from_memory)

        if tree_ids_list:
            # Загружаем все узлы.
            nodes = list(Category.objects.filter(tree_id__in=tree_ids_list))
            # Сохраняем как список для фильтрации детей
            context["all_nodes"] = nodes
            # Сохраняем как словарь для быстрого поиска родителей по ID
            context["nodes_map"] = {node.id: node for node in nodes}

    return context
