from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .views import *
from .models import UserBlock

User = get_user_model()

class BlockUserTestBase(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
        self.user2.set_password("pass")
        self.user2.save()

        self.client.force_login(self.user1)

class BlockUserTest(BlockUserTestBase):
    def block_user(self, user_id):
        url = reverse("block-user", args=[user_id])
        return self.client.post(url)
    
    def test_block_unexist_user(self):
        unexist_user_id = User.objects.latest('id').id + 1
        response = self.block_user(unexist_user_id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "존재하지 않는 유저는 차단할 수 없습니다.")
    
    def test_block_myself(self):
        response = self.block_user(self.user1.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "자기 자신을 차단할 수 없습니다.")
    
    def test_block_already_blocked_user(self):
        UserBlock.objects.create(blocker=self.user1, blocked_user=self.user2)
        response = self.block_user(self.user2.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "이미 차단된 유저입니다.")

    def test_block_user_success(self):
        response = self.block_user(self.user2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "유저가 차단되었습니다.")
        self.assertTrue(UserBlock.objects.filter(blocker=self.user1, blocked_user=self.user2).exists())
    
class UnblockUserTest(BlockUserTestBase):
    def setUp(self):
        super().setUp()
        self.user_block = UserBlock.objects.create(blocker=self.user1, blocked_user=self.user2)

    def unblock_user(self, user_id):
        url = reverse("unblock-user", args=[user_id])
        return self.client.delete(url)
    
    def test_unblock_unexist_user(self):
        unexist_user_id = User.objects.latest('id').id + 1
        response = self.unblock_user(unexist_user_id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "존재하지 않는 유저는 차단해제할 수 없습니다.")

    def test_unblock_myself(self):
        response = self.unblock_user(self.user1.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "자기 자신을 차단해제할 수 없습니다.")

    def test_unblock_not_blocked_user(self):
        self.user_block.delete()  # 명시적으로 차단 상태 제거
        response = self.unblock_user(self.user2.id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "해제할 차단이 존재하지 않습니다.")

    def test_unblock_user_success(self):
        response = self.unblock_user(self.user2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "유저 차단이 해제되었습니다.")
        self.assertFalse(UserBlock.objects.filter(blocker=self.user1, blocked_user=self.user2).exists())