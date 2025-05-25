from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='1234',
            name='테스터'
        )

    def test_login_success(self): # 로그인이 성공한 경우: 요청 온 id와 비밀번호가 DB에 존재할때
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': '1234'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login_failed(self): # 실패한 경우: 요청온 id와 비밀번호가 DB에 존재하지 않을때
        response = self.client.post(self.login_url, {
            'email': 'test@naver.com',
            'password': 'helloworld!'
        }, content_type='application/json')
        self.assertEqual(response.status_code,400)