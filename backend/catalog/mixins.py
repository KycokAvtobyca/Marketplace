from django.db.models import Model

from .models import Category


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

        # Если это action list и глубина не указана или 0,
        # нам не нужны деревья, сериализатор просто вернет пустые children
        if not depth or depth == "0":
            print("Глубина 0, деревья не нужны")
            return context

        # Получаем объекты, которые сейчас будут сериализованы
        # Это может быть страница (page) или один объект (instance)
        instances = getattr(self, "_preloaded_instances", None)

        if instances:
            # Собираем все ID категорий из объектов
            category_ids = set()
            for obj in instances:
                # Динамически получаем категорию (поддерживает вложенность типа 'sub_model__category')
                cat = obj

                for attr in self.category_relation_path.split("__"):
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
                    nodes = list(
                        Category.objects.filter(tree_id__in=tree_ids_list)
                    )
                    # Сохраняем как список для фильтрации детей
                    context["all_nodes"] = nodes
                    # Сохраняем как словарь для быстрого поиска родителей по ID
                    context["nodes_map"] = {node.id: node for node in nodes}

                # load_only_roots
                # else:
                #     print("Подгружаем только корни...")
                #     # Если нужны только корни, то достаточно загрузить их по tree_id
                #     roots = list(
                #         Category.objects.filter(
                #             tree_id__in=Category.objects.filter(
                #                 id__in=category_ids
                #             ).values("tree_id"),
                #             level=0,
                #         )
                #     )
                #     context["all_nodes"] = roots
                #     context["nodes_map"] = {node.id: node for node in roots}

        print(context["nodes_map"])
        return context

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
