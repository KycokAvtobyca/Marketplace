from catalog.utils import prefetch_tree_data


class CategoryTreeOptimizerMixin:
    """
    Миксин для автоматической подгрузки деревьев категорий.
    Работает для любых моделей, у которых есть связь с Category.
    """

    category_relation_path = "category"

    def get_serializer_context(self):
        context = super().get_serializer_context()

        # Проверяем необходимость подгрузки деревьев
        depth = self.request.query_params.get("depth")

        # Получаем объекты, которые сейчас будут сериализованы
        # Это может быть страница (page) или один объект (instance)
        instances = getattr(self, "_preloaded_instances", None)

        return prefetch_tree_data(instances, context, depth, "")

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)

        # Сохраняем страницу для использования в get_serializer_context
        if page is not None:
            self._preloaded_instances = page
        return page

    def get_object(self):
        instance = super().get_object()
        # Сохраняем одиночный объект для retrieve
        self._preloaded_instances = [instance]
        return instance
