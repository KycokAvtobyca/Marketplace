from decimal import Decimal
from unittest.mock import patch

from carts.models import Cart, CartItem
from catalog.models import Product, ProductVariant
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import Client, TestCase
from rest_framework.test import APIClient
from types import SimpleNamespace
from users.models import CustomUser, Shop

from .models import Order, OrderItem, PickupPoint
from .admin import OrderAdmin


class AdminPdfReportTests(TestCase):
    def setUp(self):
        self.seller = CustomUser.objects.create_user("89642297622")
        self.seller.is_staff = True
        self.seller.save()
        self.other_seller = CustomUser.objects.create_user("89642297623")
        self.superuser = CustomUser.objects.create_superuser(
            "89642297624", "password"
        )

        self.shop = Shop.objects.create(
            owner=self.seller,
            name="Seller Shop",
            slug="seller-shop",
            is_active=True,
        )
        self.other_shop = Shop.objects.create(
            owner=self.other_seller,
            name="Other Shop",
            slug="other-shop",
            is_active=True,
        )
        self.product = Product.objects.create(
            name="Seller Product",
            slug="seller-product",
            description="Описание тестового товара",
            shop=self.shop,
        )
        self.other_product = Product.objects.create(
            name="Other Product",
            slug="other-product",
            description="Описание другого товара",
            shop=self.other_shop,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("100.00"),
            stock=10,
            is_active=True,
        )
        self.other_variant = ProductVariant.objects.create(
            product=self.other_product,
            price=Decimal("100.00"),
            stock=10,
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.seller,
            name="Иван",
            phone_number="+79642297622",
            delivery_type=Order.DeliveryType.PICKUP,
            branch=Order.PickUpBranches.LENINA_5A,
            total_cost_without_sales=Decimal("200.00"),
            total_cost=Decimal("200.00"),
        )
        OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=1,
            price_per_item=Decimal("100.00"),
            discounted_price_per_item=Decimal("100.00"),
        )
        OrderItem.objects.create(
            order=self.order,
            product_variant=self.other_variant,
            quantity=1,
            price_per_item=Decimal("100.00"),
            discounted_price_per_item=Decimal("100.00"),
        )

    def test_shop_report_is_pdf(self):
        client = Client()
        client.force_login(self.seller)

        response = client.get("/admin/reports/shop/?download=1&all_time=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_shop_report_contains_only_seller_rows(self):
        client = Client()
        client.force_login(self.seller)

        with patch("core.admin_reports._pdf_response") as pdf_response:
            pdf_response.return_value = HttpResponse(b"ok")
            client.get("/admin/reports/shop/?download=1&all_time=1")

        sections = pdf_response.call_args.args[1]
        flat_rows = " ".join(
            str(cell)
            for section in sections
            for row in section["rows"]
            for cell in row
        )
        self.assertIn("Seller Product", flat_rows)
        self.assertNotIn("Other Product", flat_rows)

    def test_superuser_table_report_is_pdf(self):
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(Order)
        client = Client()
        client.force_login(self.superuser)

        response = client.get(
            f"/admin/reports/table/?download=1&all_time=1&content_type={content_type.pk}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_seller_cannot_reopen_closed_order_in_admin(self):
        self.order.status = Order.Status.PAID
        self.order.save(update_fields=["status"])

        admin_model = OrderAdmin(Order, admin.site)
        request = SimpleNamespace(user=self.seller)
        self.order.status = Order.Status.CREATED

        with self.assertRaises(ValidationError):
            admin_model.save_model(
                request,
                self.order,
                SimpleNamespace(changed_data=["status"]),
                True,
            )

    def test_seller_cannot_set_paid_after_receipt_in_admin(self):
        admin_model = OrderAdmin(Order, admin.site)
        request = SimpleNamespace(user=self.seller)
        self.order.status = Order.Status.PAID

        with self.assertRaises(ValidationError):
            admin_model.save_model(
                request,
                self.order,
                SimpleNamespace(changed_data=["status"]),
                True,
            )

    def test_seller_cannot_create_order_with_own_product(self):
        PickupPoint.objects.get_or_create(
            code=Order.PickUpBranches.LENINA_5A,
            defaults={
                "name": "Lenina",
                "address": "Lenina 5A",
                "is_active": True,
            },
        )
        cart, _ = Cart.objects.get_or_create(user=self.seller)
        CartItem.objects.create(cart=cart, product_variant=self.variant, quantity=1)

        client = APIClient()
        client.force_authenticate(user=self.seller)
        response = client.post(
            "/api/v1/orders/create/",
            {
                "delivery_type": Order.DeliveryType.PICKUP,
                "branch": Order.PickUpBranches.LENINA_5A,
                "name": "Иван",
                "phone_number": "+79642297622",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("cart", response.data)
