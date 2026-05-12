from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Favorite, FavoriteItem
from .serializers import FavoriteSerializer


class FavoriteViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_fav(self):
        fav, _ = Favorite.objects.get_or_create(user=self.request.user)
        return fav

    @action(detail=False, methods=["get"])
    def get_favorites(self, request):
        return Response(
            FavoriteSerializer(
                self.get_fav(), context={"request": request}
            ).data
        )

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        variant_id = request.data.get("product_variant_id")
        variant = get_object_or_404(ProductVariant, id=variant_id)
        FavoriteItem.objects.get_or_create(
            favorite=self.get_fav(), product_variant=variant
        )
        return Response(
            {
                "favorite": FavoriteSerializer(
                    self.get_fav(), context={"request": request}
                ).data
            }
        )

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        variant_id = request.data.get("product_variant_id")
        FavoriteItem.objects.filter(
            favorite=self.get_fav(), product_variant_id=variant_id
        ).delete()
        return Response(
            {
                "favorite": FavoriteSerializer(
                    self.get_fav(), context={"request": request}
                ).data
            }
        )
