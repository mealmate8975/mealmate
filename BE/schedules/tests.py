from rest_framework.test import APITestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from schedules.models import Schedules
from .schedule_service import ScheduleService
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

User = get_user_model()

### 1. API 뷰 테스트 ###
class ScheduleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="messi@example.com",
            name="Lionel Messi",
            nickname="GOAT",
            gender="0",
            password="Ronaldo"
        )
        self.client.force_authenticate(user=self.user)

        self.restaurant = Restaurant.objects.create(
            rest_name="모수",
            rest_address="이태원",
            rest_cuisine="KR"
        )

        self.schedule = Schedules.objects.create(
            rest_id=self.restaurant,
            created_by=self.user,
            schedule_name="정상회담",
            schedule_at=timezone.now() + timezone.timedelta(days=1),
            schedule_condition={"날씨": "지림", "분위기": "지림"}
        )

    def test_get_schedule_list(self):
        url = reverse("schedules:schedule-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_schedule_single(self):
        url = reverse("schedules:schedule-detail", args=[self.schedule.schedule_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_schedule(self):
        url = reverse("schedules:schedule-list-create")
        data = {
            "schedule_name": "소개팅",
            "rest_id": self.restaurant.rest_id,
            "schedule_at": (timezone.now() + timezone.timedelta(days=3)).isoformat(),
            "schedule_condition": {"날씨": "안지림", "분위기": "안좋음"}
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["schedule_name"], "소개팅")

    def test_patch_schedule(self):
        url = reverse("schedules:schedule-detail", args=[self.schedule.schedule_id])
        data = {"schedule_name": "비정상회담"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response.data["schedule_name"], "비정상회담")

    def test_delete_schedule(self):
        url = reverse("schedules:schedule-detail", args=[self.schedule.schedule_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Schedules.objects.filter(schedule_id=self.schedule.schedule_id).exists())


### 2. 서비스 계층 단위 테스트 ###
class ScheduleServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            name="Tester",
            nickname="testnick",
            gender="0"
        )
        self.restaurant = Restaurant.objects.create(
            rest_name="Test Restaurant",
            rest_address="Test Address",
            rest_cuisine="KR"
        )
        self.schedule_data = {
            "rest_id": self.restaurant.rest_id,
            "schedule_name": "Initial Schedule",
            "schedule_at": timezone.now() + timezone.timedelta(days=1),
            "schedule_condition": {"weather": "sunny"},
        }

    def test_create_schedule_success(self):
        created = ScheduleService.create_schedule(self.schedule_data, self.user)
        self.assertEqual(created["schedule_name"], self.schedule_data["schedule_name"])
        self.assertEqual(created["rest_id"], self.restaurant.rest_id)
        self.assertEqual(created["created_by"], self.user.id)

    def test_list_schedules(self):
        ScheduleService.create_schedule(self.schedule_data, self.user)
        schedules = ScheduleService.list_schedules(self.user)
        self.assertTrue(len(schedules) >= 1)
        self.assertEqual(schedules[0]["created_by"], self.user.id)

    def test_get_schedule_success(self):
        created = ScheduleService.create_schedule(self.schedule_data, self.user)
        schedule = ScheduleService.get_schedule(created["schedule_id"], self.user)
        self.assertEqual(schedule["schedule_name"], self.schedule_data["schedule_name"])

    def test_update_schedule_success(self):
        created = ScheduleService.create_schedule(self.schedule_data, self.user)
        updated_data = {"schedule_name": "Updated Name"}
        updated = ScheduleService.update_schedule(created["schedule_id"], self.user, updated_data)
        self.assertEqual(updated["schedule_name"], "Updated Name")

    def test_delete_schedule_success(self):
        created = ScheduleService.create_schedule(self.schedule_data, self.user)
        ScheduleService.delete_schedule(created["schedule_id"], self.user)
        with self.assertRaises(Exception):
            ScheduleService.get_schedule(created["schedule_id"], self.user)
    
    def test_create_schedule_optional_name(self):
        url = reverse("schedules:schedule-list-create")
        self.client.force_authenticate(user=self.user)
        data = {
            "rest_id": self.restaurant.rest_id,
            "schedule_at": timezone.now() + timezone.timedelta(days=3),
            "schedule_condition": {"날씨": "안지림", "분위기": "안좋음"}
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)  # 성공적으로 생성되어야 함