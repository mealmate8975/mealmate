from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post
from pages.models import Page

User = get_user_model()

class TestPageDetailAPIView(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
        self.user2.set_password("pass")
        self.user2.save()

        self.page = Page.objects.create(
            name = "테스트 페이지1",
            description = "테스트 페이지1의 description입니다.",
        )

        self.post1 = Post.objects.create(
            author = self.user1,
            title = "포스트1",
            content = "포스트1의 콘텐트입니다",
            type = "review",
            page = self.page,
        )

        self.post2 = Post.objects.create(
            author = self.user2,
            title = "포스트2",
            content = "포스트2의 콘텐트입니다",
            type = "tip",
            page = self.page,
        )
   
    # 성공 테스트
    def test_page_detail_includes_ordered_posts(self):
        url = reverse("pages:page-detail",kwargs={"pk":self.page.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.data["posts"]),2)
        self.assertEqual(response.data["posts"][0]["title"], "포스트2")
    
    def test_page_detail_returns_empty_posts_when_none_exist(self):
        '''
        정상 동작에 대한 경계 상황(edge case) 테스트
        '''
        page_without_posts = Page.objects.create(
            name="빈 페이지",
            description = "빈 페이지의 description입니다.",
        )
        url = reverse("pages:page-detail", kwargs={"pk": page_without_posts.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["posts"], [])
    
    # 실패 테스트
    def test_page_detail_returns_404_for_nonexistent_page(self):
        url = reverse("pages:page-detail", kwargs={"pk": 3}) # 앞 테스트의 Page(pk=2)는 삭제되었지만, pk 값 증가흔적은 다음 테스트에 영향을 줌
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    