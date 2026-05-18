from decimal import Decimal

from django.test import Client, TestCase
from rest_framework.test import APIClient
from users.models import CustomUser, Shop

from .models import (
    Attribute,
    AttributeValue,
    CatalogItemRequest,
    Category,
    Product,
    ProductTag,
    ProductType,
    ProductVariant,
)


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


class ProductCatalogFilterTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user("89642297628")
        self.shop = Shop.objects.create(
            owner=self.user,
            name="Filter Shop",
            slug="filter-shop",
            is_active=True,
        )
        self.color = Attribute.objects.create(
            name="Цвет",
            slug="color",
            is_active=True,
        )
        self.size = Attribute.objects.create(
            name="Размер",
            slug="size",
            is_active=True,
        )
        self.red = AttributeValue.objects.create(attribute=self.color, value="Красный")
        self.blue = AttributeValue.objects.create(attribute=self.color, value="Синий")
        self.large = AttributeValue.objects.create(attribute=self.size, value="L")

        self.product = Product.objects.create(
            name="Красная футболка",
            slug="red-shirt",
            description="Описание тестового товара",
            shop=self.shop,
        )
        self.matching_variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("1000.00"),
            stock=3,
            is_active=True,
        )
        self.matching_variant.attribute_values.set([self.red, self.large])

        self.other_product = Product.objects.create(
            name="Синяя футболка",
            slug="blue-shirt",
            description="Описание другого тестового товара",
            shop=self.shop,
        )
        self.other_variant = ProductVariant.objects.create(
            product=self.other_product,
            price=Decimal("1000.00"),
            stock=3,
            is_active=True,
        )
        self.other_variant.attribute_values.set([self.blue])

    def test_catalog_filters_by_attribute_values_param(self):
        response = APIClient().get(
            "/api/v1/catalog/product-catalog/",
            {"attributes": str(self.red.pk)},
        )

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["results"]}
        self.assertIn(self.product.pk, ids)
        self.assertNotIn(self.other_product.pk, ids)

    def test_catalog_filters_selected_values_on_same_variant(self):
        self.other_variant.attribute_values.add(self.large)

        response = APIClient().get(
            f"/api/v1/catalog/product-catalog/?attributes={self.red.pk}&attributes={self.large.pk}"
        )

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.product.pk})


class CatalogItemRequestTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user("89642297629")
        self.shop = Shop.objects.create(
            owner=self.user,
            name="Request Shop",
            slug="request-shop",
            is_active=True,
        )

    def test_shop_can_create_catalog_item_request_via_api(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/v1/catalog/catalog-item-requests/",
            {
                "target_type": CatalogItemRequest.TargetType.PRODUCT_TYPE,
                "name": "Платья",
                "comment": "Нужно для товаров магазина",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        request_obj = CatalogItemRequest.objects.get()
        self.assertEqual(request_obj.shop, self.shop)
        self.assertEqual(request_obj.requester, self.user)
        self.assertEqual(request_obj.status, CatalogItemRequest.Status.NEW)

    def test_approved_requests_create_catalog_objects(self):
        product_type_request = CatalogItemRequest.objects.create(
            requester=self.user,
            shop=self.shop,
            target_type=CatalogItemRequest.TargetType.PRODUCT_TYPE,
            name="Платья",
        )
        product_type_request.approve()
        self.assertTrue(ProductType.objects.filter(name="Платья").exists())

        category_request = CatalogItemRequest.objects.create(
            requester=self.user,
            shop=self.shop,
            target_type=CatalogItemRequest.TargetType.CATEGORY,
            name="Аксессуары",
        )
        category_request.approve()
        self.assertTrue(Category.objects.filter(name="Аксессуары").exists())

        tag_request = CatalogItemRequest.objects.create(
            requester=self.user,
            shop=self.shop,
            target_type=CatalogItemRequest.TargetType.PRODUCT_TAG,
            name="Новинка",
        )
        tag_request.approve()
        self.assertTrue(ProductTag.objects.filter(name="Новинка").exists())
