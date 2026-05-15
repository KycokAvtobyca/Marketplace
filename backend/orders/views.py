from api.authentication import HttpOnlyJWTAuthentication
from django.db import transaction
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from catalog.pagination import DefaultOrderPagination

from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра заказов пользователя."""

    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = DefaultOrderPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "order_items__product_variant__product",
            "order_items__product_variant__images",
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Отменить заказ. Доступно до начала сборки."""
        order = self.get_object()
        
        # Проверяем, что заказ принадлежит пользователю
        if order.user != request.user:
            return Response(
                {"detail": "Вы не можете отменить чужой заказ"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Проверяем, можно ли отменить заказ
        if order.status != Order.Status.CREATED:
            return Response(
                {
                    "detail": f"Невозможно отменить заказ со статусом '{order.get_status_display()}'. "
                    "Заказ можно отменить только до начала сборки."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Отменяем заказ
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .prefetch_related("order_items__product_variant")
                .get(pk=order.pk)
            )
            if order.status != Order.Status.CREATED:
                return Response(
                    {"detail": "Заказ уже нельзя отменить."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for item in order.order_items.all():
                item.product_variant.__class__.objects.filter(
                    pk=item.product_variant_id
                ).update(stock=F("stock") + item.quantity)

            if order.promocode_id:
                order.promocode.__class__.objects.filter(
                    pk=order.promocode_id,
                    current_usage__gt=0,
                ).update(current_usage=F("current_usage") - 1)

            order.status = Order.Status.CANCELED
            order.save(update_fields=["status", "date_time_update"])
        
        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class OrderCreateView(APIView):
    """API для создания заказа из корзины."""

    authentication_classes = [HttpOnlyJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderSerializer(order, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
