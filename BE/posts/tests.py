from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post
from pages.models import Page

User = get_user_model()

class PostTestBase(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.title = "포스트 테스트 1"
        self.content = "테스트 포스트입니다"
        self.type_ = "review"

class TestPostCreateAPIView(PostTestBase):
    # 성공 케이스 (Happy Path)
    def test_create_post_without_page_success(self):
        self.client.force_login(self.user1)
        url = reverse('posts:create_post')
        
        data = {
            "title" : self.title,
            "content": self.content,
            "type": self.type_,
        }
        response = self.client.post(url,data,format='json')
        post = Post.objects.get(title=self.title)
        self.assertEqual(response.status_code,201)
        self.assertEqual(post.content, self.content)
        self.assertEqual(post.type, "review")
        self.assertEqual(post.author, self.user1)

    def test_create_post_with_page_success(self):
        self.client.force_login(self.user1)
        page = Page.objects.create(
            name = "테스트 페이지 1",
        )
        url = reverse('posts:create_post_with_page',kwargs={'page_id' :page.id})
    
        data = {
            "title" : self.title,
            "content": self.content,
            "type": self.type_,
        }
        response = self.client.post(url,data,format='json')
        post = Post.objects.get(title=self.title)
        self.assertEqual(response.status_code,201)
        self.assertEqual(post.content, self.content)
        self.assertEqual(post.type, "review")
        self.assertEqual(post.author, self.user1)

    # 실패 케이스 (UnHappy Path)
    def test_create_post_uses_default_title_when_title_missing(self):
        self.client.force_login(self.user1)
        url = reverse('posts:create_post')
        
        data = {
            "content": self.content,
            "type": self.type_,
        }
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,201)
        post = Post.objects.filter(title="제목없음").latest('created_at')
        self.assertEqual(post.content,self.content)
        self.assertEqual(post.type,self.type_)
        
    def test_create_post_fails_with_blank_title(self):
        self.client.force_login(self.user1)
        url = reverse('posts:create_post')
        title = " "
        data = {
            "title" : title,
            "content": self.content,
            "type": self.type_,
        }
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("이 필드는 blank일 수 없습니다.", response.data["title"])
        
    def test_create_post_fails_with_missing_content(self):
        self.client.force_login(self.user1)
        url = reverse('posts:create_post')
    
        data = {
            "title" : self.title,
            "type": self.type_,
        }
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,400)
        self.assertIn("이 필드는 필수 항목입니다.", response.data["content"])

    def test_create_post_unauthenticated_returns_401(self):
        url = reverse('posts:create_post')
        
        data = {
            "title" : self.title,
            "content": self.content,
            "type": self.type_,
        }
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,401)
