from rest_framework import serializers
from users.serializers import ShopSerializer

from .models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductTag,
    ProductType,
    ProductVariant,
)


def find_root_in_memory(category_id, nodes_map):
    """Находит корень, используя только словарь в памяти"""
    current_node = nodes_map.get(category_id)
    if not current_node:
        return None

    # Предохранитель от бесконечного цикла, если в данных ошибка
    for _ in range(10):
        parent_node = nodes_map.get(current_node.parent_id)
        if not parent_node:
            return current_node
        current_node = parent_node

    return current_node


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["name", "slug", "children"]

    def get_children(self, obj):
        depth = self.context.get("depth") or "0"

        if depth is None or obj.level >= int(depth):
            return []

        all_nodes = self.context.get("all_nodes")

        # Если миксин подгрузил узлы, фильтруем их в памяти
        if all_nodes is not None:
            children = [node for node in all_nodes if node.parent_id == obj.id]
        else:
            # Фолбэк (на случай, если сериализатор вызван без миксина). N+1
            children = obj.get_children()

        return CategorySerializer(
            children, many=True, context=self.context
        ).data


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ["id"]


class ProductTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        exclude = ["id", "is_active"]


class AttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        exclude = ["id"]


class AttributeValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        exclude = ["attribute"]


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        exclude = ["id"]


class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_values = AttributeValuesSerializer(read_only=True, many=True)

    # Эти поля будут браться из аннотаций QuerySet или из @property модели
    final_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    discount_pct = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = ProductVariant
        exclude = ["price"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    brand = BrandSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    tags = ProductTagsSerializer(read_only=True, many=True)
    attributes = AttributesSerializer(read_only=True, many=True)

    def get_category(self, obj):
        nodes_map = self.context.get("nodes_map")

        # Если миксин отработал, используем только память
        if nodes_map:
            # Достаем корень без единого SQL запроса
            root = find_root_in_memory(obj.category_id, nodes_map)

            if root:
                return CategorySerializer(root, context=self.context).data

        # Фолбэк: если миксина нет или конкретной категории не оказалось в кэше
        try:
            print("конкретной категории не оказалось в кэше", obj.category.name)
            # Проверяем, есть ли категория вообще
            if obj.category_id:
                return CategorySerializer(
                    obj.category, context=self.context
                ).data
        except Exception as e:
            print(f"Error occurred while fetching category root: {e}")

        return None

    def get_variants(self, obj):
        variants_flag = self.context.get("variants_flag")

        if variants_flag:
            return ProductVariantSerializer(
                obj.variants.all(), read_only=True, many=True
            ).data
        return []

    class Meta:
        model = Product
        exclude = ["description", "updated_by"]


# class FiltersSerializer(serializers.Serializer):
#     # category Категории:
#     #     1 уровень:
#     #     ...
#     #         2 уровень:
#     #         ...
#     #             3 уровень:
#     #             ...
#     #     producttype Типы продукта: ...
#     #     brand: ...
#     #     shop: ...
#     #     attributes: ...
#     #     Цена: 0...X

#     category = serializers.SerializerMethodField()
#     product_type = ProductTypeSerializer(read_only=True, many=True)
#     brand = BrandSerializer(read_only=True, many=True)
#     shop = ShopSerializer(read_only=True, many=True)
#     attributes = AttributesSerializer(read_only=True, many=True)
#     min_price = serializers.IntegerField(min_value=0)
#     max_price = serializers.IntegerField(min_value=1)

#     def get_category(self, obj):
#         category = getattr(obj, "category", None)

#         if not category:
#             # Кэшируем дефолтный корень в контексте
#             if not self.context.get("default_root"):
#                 self.context["default_root"] = Category.objects.filter(
#                     level=0
#                 ).first()
#             category = self.context.get("default_root")

#         if not category:
#             return None

#         # Кэш для descendants – дорогая операция
#         cache_key = f"descendants_{category.id}"
#         if cache_key not in self.context:
#             root_node = category.get_root()
#             nodes = root_node.get_descendants(include_self=True).filter(
#                 level__lte=2
#             )
#             self.context[cache_key] = list(nodes)  # кэшируем

#         nodes = self.context[cache_key]
#         root_node = category.get_root()

#         custom_context = self.context.copy()
#         custom_context["all_nodes"] = nodes  # передаём в контекст
#         custom_context["depth"] = 3

#         return CategorySerializer(root_node, context=custom_context).data

#     def validate(self, data):
#         if data["min_price"] >= data["max_price"]:
#             raise serializers.ValidationError(
#                 {
#                     "min_price": "Минимальная цена не может быть больше максимальной"
#                 }
#             )

#         return data
