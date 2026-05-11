from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Favorite, FavoriteItem
from .serializers import AddToFavoriteSerializer, FavoriteSerializer


class FavoriteViewSet(viewsets.ViewSet):
    """ViewSet для управления избранным пользователя"""

    permission_classes = [IsAuthenticated]

    def get_favorite(self, user):
        """Получить или создать избранное пользователя"""
        favorite, created = Favorite.objects.get_or_create(user=user)
        return favorite

    @action(detail=False, methods=["get"])
    def get_favorites(self, request):
        """Get favorites list"""
        favorite = self.get_favorite(request.user)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Добавить товар в избранное"""
        serializer = AddToFavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_variant_id = serializer.validated_data["product_variant_id"]

        # Проверить существование варианта
        product_variant = get_object_or_404(
            ProductVariant, id=product_variant_id
        )

        favorite = self.get_favorite(request.user)

        # Добавить товар в избранное
        favorite_item, created = FavoriteItem.objects.get_or_create(
            favorite=favorite, product_variant=product_variant
        )

        if created:
            return Response(
                {
                    "message": "Товар добавлен в избранное",
                    "favorite": FavoriteSerializer(favorite).data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "Товар уже в избранном",
                    "favorite": FavoriteSerializer(favorite).data,
                },
                status=status.HTTP_200_OK,
            )

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        """Удалить товар из избранного"""
        product_variant_id = request.data.get("product_variant_id")
        if not product_variant_id:
            return Response(
                {"error": "product_variant_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite = self.get_favorite(request.user)
        favorite_item = get_object_or_404(
            FavoriteItem,
            favorite=favorite,
            product_variant_id=product_variant_id,
        )
        favorite_item.delete()

        return Response(
            {
                "message": "Товар удален из избранного",
                "favorite": FavoriteSerializer(favorite).data,
            }
        )

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """Очистить все избранное"""
        favorite = self.get_favorite(request.user)
        favorite.favorite_items.all().delete()

        return Response({"message": "Избранное очищено"})
