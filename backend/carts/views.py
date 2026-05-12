from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        print("Получаем корзину для пользователя:", self.request.user)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=["get"])
    def get_contents(self, request):
        serializer = CartSerializer(
            self.get_cart(), context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        variant_id = request.data.get("product_variant_id")
        quantity = int(request.data.get("quantity", 1))
        variant = get_object_or_404(ProductVariant, id=variant_id)

        # Проверяем, есть ли товар в наличии
        if variant.stock <= 0:
            return Response(
                {
                    "error": "Товар отсутствует в наличии"
                },
                status=400
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=self.get_cart(), product_variant=variant
        )
        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        return Response(
            {
                "message": "Добавлено",
                "cart": CartSerializer(
                    self.get_cart(), context={"request": request}
                ).data,
            }
        )

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        item_id = request.data.get("cart_item_id")
        item = get_object_or_404(CartItem, id=item_id, cart=self.get_cart())
        item.delete()
        return Response(
            {
                "cart": CartSerializer(
                    self.get_cart(), context={"request": request}
                ).data
            }
        )

    @action(detail=False, methods=["patch"])
    def update_item(self, request):
        """Обновляет количество товара в корзине."""
        item_id = request.data.get("cart_item_id")
        quantity = request.data.get("quantity")

        if quantity is None:
            return Response(
                {"error": "Параметр 'quantity' обязателен"},
                status=400
            )

        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {"error": "Количество должно быть больше 0"},
                    status=400
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Неверный формат количества"},
                status=400
            )

        item = get_object_or_404(CartItem, id=item_id, cart=self.get_cart())
        item.quantity = quantity
        item.save()

        return Response(
            {
                "message": "Обновлено",
                "cart": CartSerializer(
                    self.get_cart(), context={"request": request}
                ).data
            }
        )
