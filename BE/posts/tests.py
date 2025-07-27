from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from pages.models import Page

User = get_user_model()

class PostTestBase(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()
        self.client.force_login(self.user1)

class TestPostCreateAPIView(PostTestBase):
    def test_post_create_basic(self):
        url = reverse('posts:create_post')
        data = {
            "title" : "포스트 테스트 1",
            "content":"테스트 포스트입니다",
            "type":"review",
        }
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,201)
    def test_post_create_with_page_id(self):
        page = Page.objects.create(
            name = "테스트 페이지 1",
        )
        url = reverse('posts:create_post_with_page',kwargs={'page_id' :page.id})
        data = {
            "title" : "포스트 테스트 1",
            "content":"테스트 포스트입니다",
            "type":"review",
        }
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,201)
