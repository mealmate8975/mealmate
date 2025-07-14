from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import RealTimeLocation
from map.sse_state import get_latest_coords

from participants.models import Participants
from schedules.models import Schedules

User = get_user_model()

# class UpdateRealTimeLocationTest(APITestCase):
#     def setUp(self):
#         self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
#         self.user1.set_password("pass")
#         self.user1.save()
#         self.client.force_login(self.user1)
#     # 위도/경도 값 관련 테스트
#     # 1.경계값 테스트 (일반적인 위치 데이터는 소수점 4~6자리까지만 쓴다는 것을 고려)
#     def test_update_location_fails_with_invalid_latitude1(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": -90.000001,"longitude": 126.9780}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
#     def test_update_location_fails_with_invalid_latitude2(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": 90.000001,"longitude": 126.9780}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
#     def test_update_location_fails_with_invalid_longitude1(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": 37.5665,"longitude": -180.000001}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
#     def test_update_location_fails_with_invalid_longitude2(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": 37.5665,"longitude": 180.000001}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
#     # 2.유효하지 않은 위도/경도 값 테스트
#     def test_update_location_fails_with_non_digit_latitude(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": "no_digit","longitude": 126.9780}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])
#     def test_update_location_fails_with_invalid_longitude(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": 37.5665,"longitude": "no_digit"}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])
#     def test_update_location_fails_with_invalid_value(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": "no_digit","longitude": "no_digit"}, format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])        
#     # 실시간 좌표 생성 후 수정 테스트
#     def test_create_and_update_location(self):
#         url = reverse('map:update_real_time_location')
#         response = self.client.patch(url,{"latitude": 1,"longitude": 2}, format='json')
#         self.assertEqual(response.status_code,201)
#         self.assertIn("Coords created successfully.", response.data["message"])
#         response = self.client.patch(url,{"latitude": 37.5665,"longitude": 126.9780}, format='json')
#         self.assertEqual(response.status_code,200)

#         # 값이 잘 수정됐는지 체크
#         loc = RealTimeLocation.objects.get(user=self.user1)
#         self.assertEqual(loc.latitude, 37.5665)
#         self.assertEqual(loc.longitude, 126.9780)

#         self.assertIn("Coords updated successfully.", response.data["message"])

class RealTimeLocationStreamingTest(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()
        # 1. 스케줄 생성
        self.schedule = Schedules.objects.create(
        schedule_condition={"latitude": 0, "longitude": 0},
        created_by=self.user1
        )
        # 2. 참가자 등록
        Participants.objects.create(schedule=self.schedule, participant=self.user1)
        self.client.force_login(self.user1)
        self.schedule_id = 1
        self.url = reverse('map:update_real_time_location',kwargs={'schedule_id':self.schedule_id})
    def test_valid_location_updates_cache(self):
        """
        유효한 좌표 전송 시
        캐시에 잘 저장되는지 테스트
        """
        data = {"latitude":37.5665,"longitude":126.9780}
        response = self.client.patch(self.url, data, format='json')

        self.assertIn(response.status_code, [200, 201])
        cached = get_latest_coords()

        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0]["user_id"], self.user1.id)
        self.assertEqual(cached[0]["lat"], data["latitude"])
        self.assertEqual(cached[0]["lng"], data["longitude"])    
