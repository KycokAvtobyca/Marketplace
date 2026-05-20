from decimal import Decimal

from catalog.models import Product, ProductVariant
from django.db import connection
from django.test import TestCase
from orders.models import Order, OrderItem
from rest_framework.test import APIClient
from users.models import CustomUser, Shop

from .models import ProductComplaint, ProductQuestion, Review, ReviewComplaint


class ReviewApiTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user("89642297622")
        self.other_user = CustomUser.objects.create_user("89642297623")
        self.shop_owner = CustomUser.objects.create_user("89642297624")
        self.shop = Shop.objects.create(
            owner=self.shop_owner,
            name="Review Shop",
            slug="review-shop",
            is_active=True,
        )
        self.product = Product.objects.create(
            name="Review Product",
            slug="review-product",
            description="Описание тестового товара",
            shop=self.shop,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("500.00"),
            stock=5,
            is_active=True,
        )

    def _completed_order(self, status=Order.Status.PAID):
        order = Order.objects.create(
            user=self.user,
            status=status,
            name="Иван",
            phone_number="+79642297622",
            delivery_type=Order.DeliveryType.PICKUP,
            branch=Order.PickUpBranches.LENINA_5A,
            total_cost_without_sales=Decimal("500.00"),
            total_cost=Decimal("500.00"),
        )
        OrderItem.objects.create(
            order=order,
            product_variant=self.variant,
            quantity=1,
            price_per_item=Decimal("500.00"),
            discounted_price_per_item=Decimal("500.00"),
        )

    def test_user_can_review_only_completed_purchase_once(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/v1/reviews/",
            {
                "product_variant": self.variant.pk,
                "rating": 5,
                "description": "Очень хороший тестовый товар",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

        self._completed_order(status=Order.Status.PAID)
        response = client.post(
            "/api/v1/reviews/",
            {
                "product_variant": self.variant.pk,
                "rating": 5,
                "description": "Очень хороший тестовый товар",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)

        duplicate = client.post(
            "/api/v1/reviews/",
            {
                "product_variant": self.variant.pk,
                "rating": 4,
                "description": "Повторный отзыв недопустим",
            },
            format="json",
        )
        self.assertEqual(duplicate.status_code, 400)

    def test_user_can_review_paid_after_receipt_purchase(self):
        self._completed_order(status=Order.Status.PAID)
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/v1/reviews/",
            {
                "product_variant": self.variant.pk,
                "rating": 5,
                "description": "Товар получен и оплачен после получения, отзыв разрешен",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)

    def test_user_cannot_review_before_paid_after_receipt_status(self):
        self._completed_order(status=Order.Status.COMPLETED)
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/v1/reviews/",
            {
                "product_variant": self.variant.pk,
                "rating": 5,
                "description": "Товар получен, но еще не оплачен после получения",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_public_list_contains_only_approved_reviews(self):
        self._completed_order()
        Review.objects.create(
            user=self.user,
            product_variant=self.variant,
            rating=5,
            description="Очень хороший тестовый товар",
            status=Review.Status.PENDING,
            is_verified_purchase=True,
        )

        client = APIClient()
        response = client.get(f"/api/v1/reviews/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

        self.shop_owner.is_staff = True
        self.shop_owner.save(update_fields=["is_staff", "date_time_update"])
        seller_client = APIClient()
        seller_client.force_authenticate(user=self.shop_owner)
        response = seller_client.get(f"/api/v1/reviews/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

        review = Review.objects.get()
        review.status = Review.Status.APPROVED
        review.save(update_fields=["status"])

        response = client.get(f"/api/v1/reviews/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_author_update_sends_review_back_to_moderation_and_keeps_votes(self):
        self._completed_order()
        review = Review.objects.create(
            user=self.user,
            product_variant=self.variant,
            rating=5,
            description="Очень хороший тестовый товар",
            status=Review.Status.APPROVED,
            is_verified_purchase=True,
            useful_count=3,
            unuseful_count=1,
        )

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.patch(
            f"/api/v1/reviews/{review.pk}/",
            {
                "rating": 4,
                "description": "Обновленный отзыв после дополнительной проверки",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        review.refresh_from_db()
        self.assertEqual(review.status, Review.Status.PENDING)
        self.assertEqual(review.useful_count, 3)
        self.assertEqual(review.unuseful_count, 1)

        response = client.get(f"/api/v1/reviews/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], Review.Status.PENDING)

        response = APIClient().get(f"/api/v1/reviews/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_authenticated_user_can_report_review_and_product_once(self):
        self._completed_order()
        review = Review.objects.create(
            user=self.user,
            product_variant=self.variant,
            rating=5,
            description="Очень хороший тестовый товар",
            status=Review.Status.APPROVED,
            is_verified_purchase=True,
        )

        client = APIClient()
        client.force_authenticate(user=self.other_user)

        response = client.post(
            "/api/v1/reviews/review-complaints/",
            {"review": review.pk, "reason": "FAKE", "text": "Сомнительный отзыв"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(ReviewComplaint.objects.count(), 1)

        duplicate = client.post(
            "/api/v1/reviews/review-complaints/",
            {"review": review.pk, "reason": "FAKE"},
            format="json",
        )
        self.assertEqual(duplicate.status_code, 400)

        response = client.post(
            "/api/v1/reviews/product-complaints/",
            {
                "product": self.product.pk,
                "reason": "PROHIBITED",
                "text": "Нужно проверить товар",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(ProductComplaint.objects.count(), 1)

    def test_question_is_visible_publicly_only_after_moderation(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/v1/reviews/questions/",
            {"product": self.product.pk, "text": "Есть ли гарантия на товар?"},
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        question = ProductQuestion.objects.get()
        self.assertEqual(question.question_status, ProductQuestion.ModerationStatus.PENDING)
        self.assertFalse(question.is_public)

        anonymous = APIClient()
        response = anonymous.get(f"/api/v1/reviews/questions/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

        response = client.get(f"/api/v1/reviews/questions/?product={self.product.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["question_status"],
            ProductQuestion.ModerationStatus.PENDING,
        )

    def test_seller_answer_is_public_only_after_moderation(self):
        self.shop_owner.is_staff = True
        self.shop_owner.save(update_fields=["is_staff", "date_time_update"])
        question = ProductQuestion.objects.create(
            product=self.product,
            user=self.user,
            text="Подойдет ли товар для зимы?",
        )
        question.question_status = ProductQuestion.ModerationStatus.APPROVED
        question.save(update_fields=["question_status"])

        seller_client = APIClient()
        seller_client.force_authenticate(user=self.shop_owner)
        response = seller_client.post(
            f"/api/v1/reviews/questions/{question.pk}/answer/",
            {"answer": "Да, товар подходит для зимы."},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        question.refresh_from_db()
        self.assertEqual(question.answer_status, ProductQuestion.AnswerStatus.PENDING)
        self.assertEqual(question.answer, "")

        public_response = APIClient().get(
            f"/api/v1/reviews/questions/?product={self.product.pk}"
        )
        self.assertEqual(public_response.status_code, 200)
        self.assertEqual(public_response.data["results"][0]["answer"], "")

        seller_response = seller_client.get(
            f"/api/v1/reviews/questions/?product={self.product.pk}"
        )
        self.assertEqual(seller_response.status_code, 200)
        self.assertEqual(seller_response.data["results"][0]["answer"], "")

        question.answer_status = ProductQuestion.AnswerStatus.APPROVED
        question.save(update_fields=["answer_status"])

        public_response = APIClient().get(
            f"/api/v1/reviews/questions/?product={self.product.pk}"
        )
        self.assertEqual(public_response.status_code, 200)
        self.assertEqual(
            public_response.data["results"][0]["answer"],
            "Да, товар подходит для зимы.",
        )

    def test_question_delete_removes_legacy_answer_moderation_rows(self):
        question = ProductQuestion.objects.create(
            product=self.product,
            user=self.user,
            text="Вопрос для удаления?",
        )
        table = connection.ops.quote_name("reviews_answermoderationrequest")
        question_table = connection.ops.quote_name("reviews_productquestion")
        id_column = (
            "BIGSERIAL PRIMARY KEY"
            if connection.vendor == "postgresql"
            else "INTEGER PRIMARY KEY AUTOINCREMENT"
        )

        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            cursor.execute(
                f"CREATE TABLE {table} ("
                f"id {id_column}, "
                f"question_id bigint NOT NULL REFERENCES {question_table}(id)"
                f")"
            )
            cursor.execute(
                f"INSERT INTO {table} (question_id) VALUES (%s)",
                [question.pk],
            )

        try:
            question.delete()
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                self.assertEqual(cursor.fetchone()[0], 0)
        finally:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
