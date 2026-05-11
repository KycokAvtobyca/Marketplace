from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)


class CartViewSet(viewsets.ViewSet):
    """ViewSet для управления корзиной пользователя"""

    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        """Получить или создать корзину пользователя"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @action(detail=False, methods=["get"])
    def get_cart_contents(self, request):
        """Get cart contents"""
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Добавить товар в корзину"""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_variant_id = serializer.validated_data["product_variant_id"]
        quantity = serializer.validated_data.get("quantity", 1)

        # Проверить существование варианта
        product_variant = get_object_or_404(
            ProductVariant, id=product_variant_id
        )

        # Проверить наличие
        if product_variant.stock < quantity:
            return Response(
                {
                    "error": f"Недостаточно товара в наличии. Доступно: {product_variant.stock}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart(request.user)

        # Добавить или обновить товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_variant=product_variant
        )

        if not created:
            # Если товар уже в корзине, увеличиваем количество
            cart_item.quantity += quantity
            if cart_item.quantity > product_variant.stock:
                return Response(
                    {
                        "error": f"Недостаточно товара в наличии. Доступно: {product_variant.stock}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart_item.save()
        else:
            # Новый товар
            cart_item.quantity = quantity
            cart_item.save()

        # Очистить кэш корзины
        cart.clear_cache()

        return Response(
            {
                "message": "Товар добавлен в корзину",
                "cart": CartSerializer(cart).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["patch"])
    def update_item(self, request):
        """Обновить количество товара в корзине"""
        cart_item_id = request.data.get("cart_item_id")
        if not cart_item_id:
            return Response(
                {"error": "cart_item_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item = get_object_or_404(
            CartItem, id=cart_item_id, cart__user=request.user
        )
        quantity = serializer.validated_data["quantity"]

        # Проверить наличие
        if cart_item.product_variant.stock < quantity:
            return Response(
                {
                    "error": f"Недостаточно товара в наличии. Доступно: {cart_item.product_variant.stock}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity
        cart_item.save()

        # Очистить кэш корзины
        cart_item.cart.clear_cache()

        return Response(
            {
                "message": "Количество товара обновлено",
                "cart": CartSerializer(cart_item.cart).data,
            }
        )

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        """Удалить товар из корзины"""
        cart_item_id = request.data.get("cart_item_id")
        if not cart_item_id:
            return Response(
                {"error": "cart_item_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item = get_object_or_404(
            CartItem, id=cart_item_id, cart__user=request.user
        )
        cart = cart_item.cart
        cart_item.delete()

        # Очистить кэш корзины
        cart.clear_cache()

        return Response(
            {
                "message": "Товар удален из корзины",
                "cart": CartSerializer(cart).data,
            }
        )

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """Очистить всю корзину"""
        cart = self.get_cart(request.user)
        cart.cart_items.all().delete()
        cart.clear_cache()

        return Response({"message": "Корзина очищена"})
