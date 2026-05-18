from catalog.models import ProductVariant
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from marketing.models import PromoCode
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer


class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return (
            Cart.objects.select_related("promocode")
            .prefetch_related(
                Prefetch(
                    "cart_items__product_variant",
                    queryset=ProductVariant.objects.with_prices(
                        user=self.request.user
                    )
                    .select_related("product__brand")
                    .prefetch_related("images"),
                )
            )
            .get(pk=cart.pk)
        )

    @action(detail=False, methods=["get"])
    def get_contents(self, request):
        serializer = CartSerializer(
            self.get_cart(), context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        variant_id = request.data.get("product_variant_id")
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "Неверный формат количества"}, status=400)

        if quantity < 1:
            return Response(
                {"error": "Количество должно быть больше 0"}, status=400
            )

        variant = get_object_or_404(
            ProductVariant.objects.select_related("product__shop"),
            id=variant_id,
        )

        # Проверяем, что пользователь не может добавить свой товар
        if (
            variant.product.shop
            and variant.product.shop.owner_id == request.user.id
        ):
            return Response(
                {"error": "Вы не можете добавить свой товар в корзину"},
                status=400,
            )

        # Проверяем, есть ли товар в наличии
        if variant.stock <= 0:
            ProductVariant.sync_main_for_product(variant.product_id)
            return Response(
                {"error": "Товар отсутствует в наличии"}, status=400
            )

        cart = self.get_cart()
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            defaults={"quantity": quantity},
        )
        if not created:
            cart_item.quantity += quantity

        try:
            cart_item.full_clean()
            cart_item.save()
        except DjangoValidationError as exc:
            return Response({"error": exc.messages[0]}, status=400)

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
                {"error": "Параметр 'quantity' обязателен"}, status=400
            )

        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {"error": "Количество должно быть больше 0"}, status=400
                )
        except (ValueError, TypeError):
            return Response({"error": "Неверный формат количества"}, status=400)

        item = get_object_or_404(CartItem, id=item_id, cart=self.get_cart())
        item.quantity = quantity
        try:
            item.full_clean()
            item.save()
        except DjangoValidationError as exc:
            return Response({"error": exc.messages[0]}, status=400)

        return Response(
            {
                "message": "Обновлено",
                "cart": CartSerializer(
                    self.get_cart(), context={"request": request}
                ).data,
            }
        )

    @action(detail=False, methods=["post"])
    def apply_promocode(self, request):
        code = str(request.data.get("code", "")).strip()
        if not code:
            return Response({"promocode": "Введите промокод"}, status=400)

        promocode = PromoCode.objects.filter(code__iexact=code).first()
        if not promocode:
            return Response(
                {"promocode": "Промокод не существует."}, status=404
            )

        cart = self.get_cart()
        cart.promocode = promocode
        cart.clear_cache()

        try:
            cart.full_clean()
            cart.save()
        except DjangoValidationError as exc:
            return Response(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else {"promocode": exc.messages[0]},
                status=400,
            )

        cart = self.get_cart()
        return Response(
            {
                "message": "Промокод применен",
                "cart": CartSerializer(cart, context={"request": request}).data,
            }
        )

    @action(detail=False, methods=["post", "delete"])
    def remove_promocode(self, request):
        cart = self.get_cart()
        cart.promocode = None
        cart.save(update_fields=["promocode", "date_time_update"])
        cart.clear_cache()
        return Response(
            {
                "message": "Промокод удален",
                "cart": CartSerializer(
                    self.get_cart(), context={"request": request}
                ).data,
            }
        )

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart = self.get_cart()
        cart.cart_items.all().delete()
        cart.promocode = None
        cart.save(update_fields=["promocode", "date_time_update"])
        cart.clear_cache()
        return Response(
            {
                "message": "Корзина очищена",
                "cart": CartSerializer(
                    self.get_cart(), context={"request": request}
                ).data,
            }
        )
