from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UpdateRealTimeLocationTest(APITestCase):
    # 위도와 경도 중 하나라도 숫자가 아닐 때
    def test_update_location_fails_with_invalid_latitude(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.client.force_login(self.user1)

        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": "no_digit","longitude": 127.456}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])