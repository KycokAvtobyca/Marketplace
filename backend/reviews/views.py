from django.db import transaction
from django.db.models import F, Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.pagination import DefaultCursorPagination

from .models import ProductQuestion, Review, ReviewVote
from .serializers import ProductQuestionSerializer, ReviewSerializer


class ReviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or obj.user_id == request.user.id)
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]
    pagination_class = DefaultCursorPagination

    def get_queryset(self):
        qs = (
            Review.objects.select_related("user", "product_variant__product")
            .prefetch_related("review_images", "votes")
            .order_by("-date_time_create", "-id")
        )

        product_variant_id = self.request.query_params.get("product_variant")
        product_id = self.request.query_params.get("product")

        if product_variant_id:
            qs = qs.filter(product_variant_id=product_variant_id)
        if product_id:
            qs = qs.filter(product_variant__product_id=product_id)

        user = self.request.user
        if user and user.is_staff:
            return qs
        if product_id or product_variant_id:
            return qs.filter(status=Review.Status.APPROVED)
        if user and user.is_authenticated:
            return qs.filter(Q(status=Review.Status.APPROVED) | Q(user=user))
        return qs.filter(status=Review.Status.APPROVED)

    def perform_update(self, serializer):
        if serializer.instance.user_id == self.request.user.id:
            serializer.save(status=Review.Status.PENDING)
            return
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        value = request.data.get("value")
        if value not in [ReviewVote.Value.USEFUL, ReviewVote.Value.UNUSEFUL]:
            return Response(
                {"value": "Передайте USEFUL или UNUSEFUL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            review = Review.objects.select_for_update().get(pk=self.get_object().pk)
            if review.user_id == request.user.id:
                return Response(
                    {"detail": "Нельзя голосовать за свой отзыв."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vote, created = ReviewVote.objects.select_for_update().get_or_create(
                review=review,
                user=request.user,
                defaults={"value": value},
            )
            if created:
                field = "useful_count" if value == ReviewVote.Value.USEFUL else "unuseful_count"
                Review.objects.filter(pk=review.pk).update(**{field: F(field) + 1})
            elif vote.value != value:
                old_field = (
                    "useful_count"
                    if vote.value == ReviewVote.Value.USEFUL
                    else "unuseful_count"
                )
                new_field = "useful_count" if value == ReviewVote.Value.USEFUL else "unuseful_count"
                vote.value = value
                vote.save(update_fields=["value", "date_time_update"])
                Review.objects.filter(pk=review.pk).update(
                    **{
                        old_field: F(old_field) - 1,
                        new_field: F(new_field) + 1,
                    }
                )

            review.refresh_from_db()

        return Response(ReviewSerializer(review, context={"request": request}).data)


class ProductQuestionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or obj.user_id == request.user.id)
        )


class ProductQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductQuestionSerializer
    permission_classes = [ProductQuestionPermission]
    pagination_class = DefaultCursorPagination

    def get_queryset(self):
        qs = ProductQuestion.objects.select_related(
            "user",
            "answered_by",
            "product",
            "product__shop",
        ).order_by("-date_time_create", "-id")

        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)

        user = self.request.user
        if user and user.is_staff:
            if user.is_superuser:
                return qs
            return qs.filter(Q(is_public=True) | Q(product__shop__owner=user))
        if user and user.is_authenticated:
            return qs.filter(Q(is_public=True) | Q(user=user))
        return qs.filter(is_public=True)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def answer(self, request, pk=None):
        question = self.get_object()
        shop = question.product.shop
        can_answer = request.user.is_superuser or (
            request.user.is_staff and shop and shop.owner_id == request.user.id
        )
        if not can_answer:
            return Response(
                {"detail": "Ответить может только продавец этого товара."},
                status=status.HTTP_403_FORBIDDEN,
            )

        answer = (request.data.get("answer") or "").strip()
        if len(answer) < 2:
            return Response(
                {"answer": "Введите ответ продавца."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question.set_answer(request.user, answer)
        return Response(
            ProductQuestionSerializer(question, context={"request": request}).data
        )
