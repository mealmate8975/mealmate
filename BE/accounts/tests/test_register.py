from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import CustomUser

class RegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('accounts:register')  # URL 네임스페이스에 맞게 조정

    # 회원가입 성공하는 테스트 코드입니다.
    def test_register_success(self):
        response = self.client.post(self.register_url, {
            'email': 'registertest@example.com',
            'password': '1111',
            'name': '회원가입 테스트',
            'phone': '01012345678'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(email='registertest@example.com').exists())

    # 이메일은 필수입력이라 없으면 에러가 뜨는지 확인하는 코드입니다.
    def test_register_no_email(self):
        response = self.client.post(self.register_url, {
            'password': 'password',
            'name': '이름있음',
            'phone': '01056781234'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # 전화번호 형식 테스트입니다.
    def test_register_phone_number_format(self):
        response = self.client.post(self.register_url, {
            'email': 'invalidphone@example.com',
            'password': '1234',
            'name': '전화번호테스트',
            'phone': '010102039209'  # 형식이 잘못된 전화번호
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)
