from django.test import Client, TestCase

from users.models import CustomUser, Shop

from .models import Category, ProductType


class AdminAutocompleteTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            "89642297627",
            password="test-pass",
            is_staff=True,
        )
        Shop.objects.create(owner=self.user, name="Shop")
        self.client = Client()
        self.client.force_login(self.user)

    def test_shop_staff_can_autocomplete_product_category(self):
        Category.objects.create(name="Одежда", slug="odezhda")

        response = self.client.get(
            "/admin/autocomplete/",
            {
                "app_label": "catalog",
                "model_name": "product",
                "field_name": "category",
                "term": "Одеж",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["text"], "Одежда")

    def test_shop_staff_can_autocomplete_product_type(self):
        ProductType.objects.create(name="Толстовки", slug="tolstovki")

        response = self.client.get(
            "/admin/autocomplete/",
            {
                "app_label": "catalog",
                "model_name": "product",
                "field_name": "product_type",
                "term": "Толст",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["text"], "Толстовки")
