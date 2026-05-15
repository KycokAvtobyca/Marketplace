from decimal import Decimal

from carts.models import Cart, CartItem
from catalog.models import Product, ProductVariant
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient
from django.test import TestCase
from users.models import CustomUser, Shop

from .models import Discount, PromoCode


class PromoCodeLogicTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user("89642297622")
        self.shop_owner = CustomUser.objects.create_user("89642297623")
        self.shop_owner.is_staff = True
        self.shop_owner.save(update_fields=["is_staff"])
        self.other_shop_owner = CustomUser.objects.create_user("89642297624")
        self.shop = Shop.objects.create(
            owner=self.shop_owner,
            name="Promo Shop",
            slug="promo-shop",
            is_active=True,
        )
        self.other_shop = Shop.objects.create(
            owner=self.other_shop_owner,
            name="Other Promo Shop",
            slug="other-promo-shop",
            is_active=True,
        )
        self.product = Product.objects.create(
            name="Promo Product",
            slug="promo-product",
            description="Описание тестового товара",
            shop=self.shop,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("1000.00"),
            stock=10,
            is_active=True,
        )
        self.other_shop_product = Product.objects.create(
            name="Other Shop Product",
            slug="other-shop-product",
            description="Описание товара другого магазина",
            shop=self.other_shop,
        )
        self.other_shop_variant = ProductVariant.objects.create(
            product=self.other_shop_product,
            price=Decimal("900.00"),
            stock=10,
            is_active=True,
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=self.cart, product_variant=self.variant, quantity=2
        )

    def _promocode(self, **kwargs):
        defaults = {
            "code": "SALE10",
            "is_active": True,
            "is_global": True,
            "discount_percentage": Decimal("0.10"),
            "usage_limit": 10,
            "min_amount": Decimal("10.00"),
        }
        defaults.update(kwargs)
        return PromoCode.objects.create(**defaults)

    def test_percentage_promocode_discounts_cart_total(self):
        promo = self._promocode()
        self.cart.promocode = promo
        self.cart.clear_cache()

        self.assertEqual(self.cart.total_items_price, Decimal("2000.00"))
        self.assertEqual(self.cart.total_cost, Decimal("1800.0000"))

    def test_fixed_promocode_discounts_cart_total(self):
        promo = self._promocode(
            code="FIXED",
            discount_percentage=Decimal("0.00"),
            amount=Decimal("300.00"),
        )
        self.cart.promocode = promo
        self.cart.clear_cache()

        self.assertEqual(self.cart.total_cost, Decimal("1700.00"))

    def test_product_promocode_discounts_only_eligible_items(self):
        other_product = Product.objects.create(
            name="Other Promo Product",
            slug="other-promo-product",
            description="Описание второго тестового товара",
            shop=self.shop,
        )
        other_variant = ProductVariant.objects.create(
            product=other_product,
            price=Decimal("500.00"),
            stock=10,
            is_active=True,
        )
        CartItem.objects.create(
            cart=self.cart, product_variant=other_variant, quantity=1
        )

        promo = self._promocode(
            code="ONLYPRODUCT",
            is_global=False,
            product=self.product,
        )
        self.cart.promocode = promo
        self.cart.clear_cache()

        self.assertEqual(self.cart.total_items_price, Decimal("2500.00"))
        self.assertEqual(self.cart.total_cost, Decimal("2300.0000"))

    def test_promocode_excluded_product_is_rejected_for_cart(self):
        promo = self._promocode(code="EXCLUDED")
        promo.excluded_products.add(self.product)
        self.cart.promocode = promo
        self.cart.clear_cache()

        with self.assertRaises(ValidationError):
            self.cart.full_clean()

    def test_discount_excluded_variant_is_not_applied_to_catalog_price(self):
        discount = Discount.objects.create(
            name="Global discount",
            is_global=True,
            is_active=True,
            discount_percentage=Decimal("0.20"),
        )
        discount.excluded_variants.add(self.variant)

        variant = ProductVariant.objects.with_prices().get(pk=self.variant.pk)

        self.assertEqual(variant.discount_pct, Decimal("0"))
        self.assertEqual(variant.final_price, Decimal("1000.00"))

    def test_shop_owner_can_create_promocode_only_for_own_product(self):
        client = APIClient()
        client.force_authenticate(user=self.shop_owner)

        response = client.post(
            "/api/v1/marketing/promocodes/",
            {
                "code": "SHOP10",
                "product": self.product.pk,
                "discount_percentage": "0.10",
                "usage_limit": 5,
                "min_amount": "10.00",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        promo = PromoCode.objects.get(code="SHOP10")
        self.assertEqual(promo.product_id, self.product.pk)
        self.assertFalse(promo.is_global)

        response = client.post(
            "/api/v1/marketing/promocodes/",
            {
                "code": "OTHER10",
                "product": self.other_shop_product.pk,
                "discount_percentage": "0.10",
                "usage_limit": 5,
                "min_amount": "10.00",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403, response.data)

    def test_promocode_rejects_min_amount_expiration_and_usage_limit(self):
        min_amount_promo = self._promocode(code="MIN", min_amount=Decimal("3000.00"))
        self.assertFalse(
            min_amount_promo.can_use_check(
                user=self.user, order_total=Decimal("2000.00")
            )[0]
        )

        expired = self._promocode(
            code="OLD",
            valid_to=timezone.now() - timezone.timedelta(days=1),
        )
        self.assertFalse(
            expired.can_use_check(user=self.user, order_total=Decimal("2000.00"))[0]
        )

        limited = self._promocode(code="LIMIT", usage_limit=1, current_usage=1)
        self.assertFalse(
            limited.can_use_check(user=self.user, order_total=Decimal("2000.00"))[0]
        )

    def test_order_creation_moves_promocode_from_cart_and_increments_usage(self):
        promo = self._promocode(code="ORDER")
        self.cart.promocode = promo
        self.cart.save()

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            "/api/v1/orders/create/",
            {
                "delivery_type": "PICKUP",
                "branch": "LENINA_5A",
                "name": "Иван",
                "phone_number": "89642297622",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        promo.refresh_from_db()
        self.cart.refresh_from_db()
        self.assertEqual(promo.current_usage, 1)
        self.assertIsNone(self.cart.promocode_id)
        self.assertEqual(response.data["promocode"], promo.pk)
