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

# class TestPostCreateAPIView(PostTestBase):
#     # 성공 케이스 (Happy Path)
#     def test_create_post_without_page_success(self):
#         self.client.force_login(self.user1)
#         url = reverse('posts:create_post')
        
#         data = {
#             "title" : self.title,
#             "content": self.content,
#             "type": self.type_,
#         }
#         response = self.client.post(url,data,format='json')
#         post = Post.objects.get(title=self.title)
#         self.assertEqual(response.status_code,201)
#         self.assertEqual(post.content, self.content)
#         self.assertEqual(post.type, "review")
#         self.assertEqual(post.author, self.user1)

#     def test_create_post_with_page_success(self):
#         self.client.force_login(self.user1)
#         page = Page.objects.create(
#             name = "테스트 페이지 1",
#         )
#         url = reverse('posts:create_post_with_page',kwargs={'page_id' :page.id})
    
#         data = {
#             "title" : self.title,
#             "content": self.content,
#             "type": self.type_,
#         }
#         response = self.client.post(url,data,format='json')
#         post = Post.objects.get(title=self.title)
#         self.assertEqual(response.status_code,201)
#         self.assertEqual(post.content, self.content)
#         self.assertEqual(post.type, "review")
#         self.assertEqual(post.author, self.user1)

#     # 실패 케이스 (UnHappy Path)
#     def test_create_post_uses_default_title_when_title_missing(self):
#         self.client.force_login(self.user1)
#         url = reverse('posts:create_post')
        
#         data = {
#             "content": self.content,
#             "type": self.type_,
#         }
#         response = self.client.post(url,data,format='json')
#         self.assertEqual(response.status_code,201)
#         post = Post.objects.filter(title="제목없음").latest('created_at')
#         self.assertEqual(post.content,self.content)
#         self.assertEqual(post.type,self.type_)
        
#     def test_create_post_fails_with_blank_title(self):
#         self.client.force_login(self.user1)
#         url = reverse('posts:create_post')
#         title = " "
#         data = {
#             "title" : title,
#             "content": self.content,
#             "type": self.type_,
#         }
#         response = self.client.post(url,data,format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("이 필드는 blank일 수 없습니다.", response.data["title"])
        
#     def test_create_post_fails_with_missing_content(self):
#         self.client.force_login(self.user1)
#         url = reverse('posts:create_post')
    
#         data = {
#             "title" : self.title,
#             "type": self.type_,
#         }
#         response = self.client.post(url,data,format='json')
#         self.assertEqual(response.status_code,400)
#         self.assertIn("이 필드는 필수 항목입니다.", response.data["content"])

#     def test_create_post_unauthenticated_returns_401(self):
#         url = reverse('posts:create_post')
        
#         data = {
#             "title" : self.title,
#             "content": self.content,
#             "type": self.type_,
#         }
#         response = self.client.post(url,data,format='json')
#         self.assertEqual(response.status_code,401)
#         # 이미지 파일 테스트도 필요

# class TestPostListAPIView(PostTestBase):
#     def setUp(self):
#         super().setUp()

#         self.page1 = Page.objects.create(
#             name = "테스트 페이지1",
#             description = "테스트 페이지1입니다.",
#         )

#         self.page2 = Page.objects.create(
#             name = "테스트 페이지2",
#             description = "테스트 페이지2입니다.",
#         )
    
#     def test_post_list_returns_401_for_unauthenticated_user(self):
#         url = reverse("posts:post_list")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code,401)
    
#     def test_post_list_returns_empty_list_when_no_posts_exist(self):
#         self.client.force_login(self.user1)
#         url = reverse("posts:post_list")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code,200)
#         self.assertEqual(response.data, [])

#     def test_post_list_returns_all_posts_for_authenticated_user(self):
#         self.user2 = User(email="user2@example.com", name="User One", nickname="user2", gender='1')
#         self.user2.set_password("pass")
#         self.user2.save()

#         self.post1 = Post.objects.create(
#             author = self.user1,
#             title = self.title,
#             content = self.content,
#             type = self.type_,
#         )

#         self.post2 = Post.objects.create(
#             author = self.user2,
#             page_id = self.page1.id,
#             title = "테스트 포스트2",
#             content = "테스트 포스트2입니다.",
#             type = "review",
#         )

#         self.post3 = Post.objects.create(
#             author = self.user1,
#             page_id = self.page2.id,
#             title = "테스트 포스트3",
#             content = "테스트 포스트3입니다.",
#             type = "tip",
#         )

#         self.client.force_login(self.user1)
#         url = reverse("posts:post_list")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code,200)
#         self.assertEqual(len(response.data),3)
#         self.assertEqual(response.data[0]["title"], self.post3.title)  # 최신순 검증
#         self.assertEqual(response.data[-1]["title"], self.post1.title)

class TestPostUpdateAPIView(PostTestBase):
    def setUp(self):
        super().setUp()

        self.post1 = Post.objects.create(
            author = self.user1,
            title = self.title,
            content = self.content,
            type = self.type_,
        )

        self.title2 = "포스트 수정 테스트1"
        self.content2 = "포스트 수정 테스트입니다."
        self.type_2 = "tip"

#     # 실패 케이스 (UnHappy Path) 
#     def test_post_update_for_unauthenticated_user(self):
#         url = reverse("posts:post_update",kwargs={"pk":self.post1.id})
#         data = {
#             "title" : self.title2,
#             "content" :self.content2,
#             "type" : self.type_2, 
#         }
#         response = self.client.patch(url,data,format='json')
#         self.assertEqual(response.status_code,401)
    
    # 성공 케이스 (Happy Path)
    def test_authenticated_user_can_update_post(self):
        self.client.force_login(self.user1)
        url = reverse("posts:post_update",kwargs={"pk":self.post1.id})
        data = {
            "title" : self.title2,
            "content" :self.content2,
            "type" : self.type_2, 
        }
        response = self.client.patch(url,data,format='json')
        self.assertEqual(response.status_code,200)
        self.post1.refresh_from_db() # 값 업데이트
        self.assertEqual(self.post1.title, self.title2)
        self.assertEqual(self.post1.content, self.content2)
        self.assertEqual(self.post1.type, self.type_2)