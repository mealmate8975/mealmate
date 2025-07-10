from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UpdateRealTimeLocationTest(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()
        self.client.force_login(self.user1)
    # 위도 관련 테스트
    # 경계값 테스트 (일반적인 위치 데이터는 소수점 4~6자리까지만 쓴다는 것을 고려)
    def test_update_location_fails_with_invalid_latitude1(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": -90.000001,"longitude": 127.456}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_latitude2(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": 90.000001,"longitude": 127.456}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_longitude1(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": 38,"longitude": -180.000001}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_longitude2(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": 38,"longitude": 180.000001}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    # 유효하지 않은 위도와 경도 테스트
    def test_update_location_fails_with_non_digit_latitude(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": "no_digit","longitude": 127.456}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_longitude(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": 38,"longitude": "no_digit"}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_value(self):
        url = reverse('map:update_real_time_location')
        response = self.client.patch(url,{"latitude": "no_digit","longitude": "no_digit"}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])

    