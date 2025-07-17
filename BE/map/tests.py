from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import RealTimeLocation
from map.sse_state import get_latest_coords
import json
from map.sse_state import set_latest_coords

from participants.models import Participants
from schedules.models import Schedules

User = get_user_model()

class TestRealTimeLocationDBWrite(APITestCase):
    """
    위치 업데이트 API의 유효성 검증 (숫자 타입, 범위)
	실시간 위치 좌표가 DB에 정상 생성/수정되는지 확인
    """
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.schedule = Schedules.objects.create(
            schedule_condition={"latitude": 0, "longitude": 0},
            created_by=self.user1
        )
        Participants.objects.create(schedule=self.schedule, participant=self.user1)

        self.client.force_login(self.user1)
    # 위도/경도 값 관련 테스트
    # 1.경계값 테스트 (일반적인 위치 데이터는 소수점 4~6자리까지만 쓴다는 것을 고려)
    def test_update_location_fails_with_invalid_latitude1(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": -90.000001,"longitude": 126.9780}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_latitude2(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": 90.000001,"longitude": 126.9780}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_longitude1(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": 37.5665,"longitude": -180.000001}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_longitude2(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": 37.5665,"longitude": 180.000001}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도는 -90~90, 경도는 -180~180 사이여야 합니다.", response.data["detail"])
    # 2.유효하지 않은 위도/경도 값 테스트
    def test_update_location_fails_with_non_digit_latitude(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": "no_digit","longitude": 126.9780}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_longitude(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": 37.5665,"longitude": "no_digit"}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])
    def test_update_location_fails_with_invalid_value(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": "no_digit","longitude": "no_digit"}, format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])        
    # 실시간 좌표 생성 후 수정 테스트
    def test_create_and_update_location(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url,{"latitude": 1,"longitude": 2}, format='json')
        self.assertEqual(response.status_code,201)
        self.assertIn("Coords created successfully.", response.data["message"])
        response = self.client.patch(url,{"latitude": 37.5665,"longitude": 126.9780}, format='json')
        self.assertEqual(response.status_code,200)

        # 값이 잘 수정됐는지 체크
        loc = RealTimeLocation.objects.get(user=self.user1)
        self.assertEqual(loc.latitude, 37.5665)
        self.assertEqual(loc.longitude, 126.9780)

        self.assertIn("Coords updated successfully.", response.data["message"])

    def test_update_location_fails_with_none_latitude(self):
        url = reverse('map:update_real_time_location', kwargs={'schedule_id': self.schedule.schedule_id})
        response = self.client.patch(url, {"latitude": None, "longitude": 126.9780}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("위도와 경도는 숫자여야 합니다.", response.data["detail"])

class TestRealTimeLocationCacheUpdate(APITestCase):
    """
    위치 전송 시 캐시(_latest_coords)가 갱신되는지 확인
    """
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.schedule = Schedules.objects.create(
        schedule_condition={"latitude": 0, "longitude": 0},
        created_by=self.user1
        )

        Participants.objects.create(schedule=self.schedule, participant=self.user1)
        self.client.force_login(self.user1)
        self.url = reverse('map:update_real_time_location',kwargs={'schedule_id':self.schedule.schedule_id})
    def test_valid_location_updates_cache(self):
        # PATCH 요청 → get_latest_coords() 로 확인
        '''
        유효한 좌표 전송 시
        캐시에 잘 저장되는지 테스트
        '''
        data = {"latitude":37.5665,"longitude":126.9780}
        response = self.client.patch(self.url, data, format='json')

        self.assertIn(response.status_code, [200, 201])
        cached = get_latest_coords()

        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0]["user_id"], self.user1.id)
        self.assertEqual(cached[0]["lat"], data["latitude"])
        self.assertEqual(cached[0]["lng"], data["longitude"])

class TestSSECoordinateStream(APITestCase):
    """
    SSE 응답 형식 및 데이터 포함 여부 확인
	여러 유저 위치 전송 시 캐시에 모두 반영되는지 확인
	빈 캐시일 때의 응답 처리 확인
	SSE 재연결 시 응답 일관성 확인
    """
    def setUp(self):
        self.user = User.objects.create_user(email="sse@example.com", password="1234",nickname="user1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="1234",nickname="user2")

        self.client.force_login(self.user)

        # 스케줄 및 참가자 생성
        self.schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={"latitude": 0, "longitude": 0}
        )
        Participants.objects.create(schedule=self.schedule, participant=self.user)
        Participants.objects.create(schedule=self.schedule, participant=self.user2)

        # 위치 등록 → 캐시에 올라가도록 유도
        self.client.patch(
            reverse("map:update_real_time_location", kwargs={"schedule_id": self.schedule.schedule_id}),
            {"latitude": 37.5, "longitude": 127.0},
            format="json"
        )

        # user2로 로그인 후 위치 전송
        self.client.logout()
        self.client.force_login(self.user2)
        self.client.patch(
            reverse("map:update_real_time_location", kwargs={"schedule_id": self.schedule.schedule_id}),
            {"latitude": 38.0, "longitude": 128.0},
            format="json"
        )
    def test_sse_response_contains_latest_coords(self):
        response = self.client.get("/api/map/location/stream/", follow=True)

        self.assertEqual(response.status_code, 200)
        first_chunk = next(response.streaming_content)
        decoded = first_chunk.decode("utf-8")

        self.assertTrue(decoded.startswith("data:"))
        self.assertIn("lat", decoded)
        self.assertIn("lng", decoded)
        self.assertIn("user_id", decoded)

        # SSE 프로토콜은 data: ... \n\n 이어야 함
        self.assertTrue(decoded.endswith("\n\n"))
    
    def test_multiple_users_coords_are_cached(self):
        cached = get_latest_coords()
        self.assertEqual(len(cached), 2)

        user_ids = [coord["user_id"] for coord in cached]
        self.assertIn(self.user.id, user_ids)
        self.assertIn(self.user2.id, user_ids)
    
    def test_sse_response_when_cache_is_empty(self):
        """
        캐시가 비어 있는 경우 SSE 응답이 빈 리스트인 data:[]\n\n 형식인지 확인
        """
        # 캐시 비우기
        set_latest_coords([])  # 테스트 시작 전 캐시를 강제로 비워야 함 -> 위치 공유를 아무도 시작하지 않은 상태를 시뮬레이션 하기 위함

        # SSE 요청 보내기
        url = reverse("map:stream_location")
        response = self.client.get(url, follow=True) # follow=True는 리디렉션이 있다면 따라가게 함

        # 응답 파싱 후 검증
        first_chunk = next(response.streaming_content) # Django의 StreamingHttpResponse는 스트리밍 데이터이므로,응답 본문 전체가 한 번에 오지 않고 chunk(조각) 단위로 전달됨
        decoded = first_chunk.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(decoded.startswith("data:["))
        self.assertIn("[]", decoded)
        self.assertTrue(decoded.endswith("\n\n"))

    # 사용자가 네트워크 문제나 페이지 이동으로 인해 SSE 연결이 끊겼다가 다시 연결될 수 있음, 이때 서버는 지금까지 저장된 최신 위치 정보를 동일하게 응답해야 함
    def test_sse_reconnect_returns_latest_coords(self): 
        """
        SSE를 재요청해도 항상 최신 좌표가 응답되는지 확인
        """
        # 첫 번째 SSE 응답 받기
        url = reverse("map:stream_location")
        response1 = self.client.get(url, follow=True)
        first_chunk = next(response1.streaming_content)
        decoded1 = first_chunk.decode("utf-8")
        # 두 번째 SSE 요청 및 응답 받기
        response2 = self.client.get(url, follow=True)
        second_chunk = next(response2.streaming_content)
        decoded2 = second_chunk.decode("utf-8")
        # 두 응답이 동일한지 검증
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        self.assertEqual(decoded1, decoded2) # 	응답 내용이 완전히 같아야 함 → 재연결된 경우에도 캐시된 좌표가 그대로 유지되어야 하기 때문

        self.assertTrue(decoded1.startswith("data:")) # "data:"로 시작하고
        self.assertTrue(decoded1.endswith("\n\n")) # \n\n으로 끝나야 하고
        self.assertIn("lat", decoded1)
        self.assertIn("lng", decoded1)
        # 좌표 데이터(lat, lng)가 포함되어 있어야 함

class TestScheduleLocationAPI(APITestCase):
    """
    약속 장소(schedule_condition)에 저장된 위도·경도 좌표가
    클라이언트가 요청했을 때 정확히 반환되는지 확인하는 테스트
    """
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="1234",nickname="user")

    def test_place_location_404_if_unauthorized(self):
        self.schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={"latitude": 37.5665, "longitude": 126.9780}
        )

        url = reverse("map:schedule_place_location", kwargs={"schedule_id": self.schedule.schedule_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_place_location_404_if_schedule_does_not_exist(self):
        self.client.force_login(self.user)
        url = reverse("map:schedule_place_location", kwargs={"schedule_id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

        
    def test_get_schedule_location_coords(self):
        self.client.force_login(self.user)
        self.schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={"latitude": 37.5665, "longitude": 126.9780}
        )

        url = reverse("map:schedule_place_location", kwargs={"schedule_id": self.schedule.schedule_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("lat", response.data)
        self.assertIsInstance(response.data["lat"], float)
        self.assertIn("lng", response.data)
        self.assertIsInstance(response.data["lng"], float)
    
    # 1. lat은 유효하지만 lng는 문자열인 경우
    def test_schedule_location_with_valid_lat_and_invalid_lng(self):
        self.client.force_login(self.user)
        schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={"latitude": 37.5665, "longitude": "invalid"}
        )
        url = reverse("map:schedule_place_location", kwargs={"schedule_id": schedule.schedule_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("lng", response.data)
    
    #2. lat이 없고 lng만 있는 경우
    def test_schedule_location_with_missing_latitude(self):
        self.client.force_login(self.user)
        schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={"longitude": 126.9780}
        )
        url = reverse("map:schedule_place_location", kwargs={"schedule_id": schedule.schedule_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("lat", response.data)
    
    # 3. lat과 lng 모두 누락된 경우
    def test_schedule_location_with_no_coordinates(self):
        self.client.force_login(self.user)
        schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={}
        )
        url = reverse("map:schedule_place_location", kwargs={"schedule_id": schedule.schedule_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("lat", response.data)
        self.assertIn("lng", response.data)
    
    # 4. lat=None, lng=None 인 경우
    def test_schedule_location_with_null_coordinates(self):
        self.client.force_login(self.user)
        schedule = Schedules.objects.create(
            created_by=self.user,
            schedule_condition={"latitude": None, "longitude": None}
        )
        url = reverse("map:schedule_place_location", kwargs={"schedule_id": schedule.schedule_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("lat", response.data)
        self.assertIn("lng", response.data)
                         