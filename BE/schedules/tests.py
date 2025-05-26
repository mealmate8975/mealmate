from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from django.urls import reverse
from .models import Schedules
from django.utils import timezone

"""로그인된 사용자의 스케줄 조회(전체, 단일)"""
"""스케줄 생성(생성자는 로그인된 사용자)"""
"""스케줄 수정(부분 수정)"""
"""스케줄 삭제"""

User = get_user_model()

class ScheduleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email = "messi@example.com",
            name = 'Lionel Messi',
            nickname = "GOAT",
            gender = "0",
            password = "Ronaldo"
        )
        self.user.save()
        self.client.login(email="messi@example.com", password="Ronaldo")

        self.restaurant = Restaurant.objects.create(
            rest_name = "모수",
            rest_address = "이태원",
            rest_cuisine = "KR"
        )

        self.schedule = Schedules.objects.create(
            rest_id = self.restaurant,
            created_by = self.user,
            schedule_name = "정상회담",
            created_at = timezone.now(),
            schedule_at = timezone.now() + timezone.timedelta(days=1),
            schedule_condition = {"날씨" : "지림", '분위기' : '지림'}
        )

    """스케줄 조회(전체)"""
    def test_get_schedule_list(self):
        url = reverse("schedules:schedule-list-create")
        response = self.client.get(url)
        print(f"스케줄 전체 조회 : {response.data}")
        self.assertEqual(response.status_code, 200)

    """스케줄 조회(단일)"""
    def test_get_schedule_single(self):
        url = reverse("schedules:schedule-detail", args=[self.schedule.schedule_id])
        response = self.client.get(url)
        print(f"스케줄 단일 조회 : {response.data}")
        self.assertEqual(response.status_code, 200)
        

    """스케줄 생성"""
    def test_create_schedule(self):
        url = reverse("schedules:schedule-list-create")
        data = {
            'schedule_name' : '소개팅',
            'rest_id' : self.restaurant.rest_id,
            'schedule_at' : timezone.now() + timezone.timedelta(days=3),
            'schedule_condition' : {'날씨' : '안지림', '분위기' : '안좋음'}
        }
        response = self.client.post(url, data, format = 'json')
        print(f"스케줄 생성 : {response.data}")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["schedule_name"], "소개팅")

    """스케줄 수정(patch) 테스트 코드"""
    def test_patch_schedule(self):
        url = reverse("schedules:schedule-detail", args=[self.schedule.schedule_id])
        data = {'schedule_name' : '비정상회담'}
        response = self.client.patch(url, data, format='json')
        print(f"스케줄 수정: {response.data}")
        self.assertEqual(response.data["schedule_name"], "비정상회담")
        self.assertEqual(response.status_code, 206)

    """스케줄 삭제 테스트 코드"""
    def test_delete_schedule(self):
        url = reverse("schedules:schedule-detail", args=[self.schedule.schedule_id])
        response = self.client.delete(url)
        print(f"스케줄 삭제 : {response.data}")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Schedules.objects.filter(schedule_id = self.schedule.schedule_id).exists())
