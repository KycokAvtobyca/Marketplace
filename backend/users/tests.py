from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, PhoneBan, SMSCode


class PhoneBanTests(TestCase):
    def test_banned_phone_cannot_request_sms_or_token(self):
        PhoneBan.objects.create(phone_number="89642297631", reason="test")
        client = APIClient()

        response = client.post(
            "/api/v1/users/auth/send-sms/",
            {"phone_number": "89642297631"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"]["code"], "user_blocked")

        SMSCode.objects.create(phone_number="+79642297631", code="123456")
        response = client.post(
            "/api/v1/users/auth/token/",
            {"phone_number": "89642297631", "sms_code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"]["code"], "user_blocked")

    def test_banned_existing_user_cannot_use_authenticated_api(self):
        user = CustomUser.objects.create_user("89642297632")
        PhoneBan.objects.create(phone_number="89642297632", reason="test")
        client = APIClient()
        token = RefreshToken.for_user(user).access_token
        client.cookies["access_token"] = str(token)

        response = client.get("/api/v1/users/profile/")
        self.assertEqual(response.status_code, 401)
        detail = response.data.get("detail", response.data)
        self.assertEqual(detail["code"], "user_blocked")
