from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from .models import Friendship

User = get_user_model()

class SendFriendRequestTest(APITestCase):  # APITestCase를 상속받아 테스트 케이스 클래스를 정의
    def setUp(self):  # 각 테스트 메서드가 실행되기 전에 호출되는 메서드
        # 첫 번째 사용자 생성
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')  # User 객체 생성
        self.user1.set_password("pass")  # 비밀번호를 해시화하여 설정
        self.user1.save()  # 사용자 객체를 데이터베이스에 저장

        # 두 번째 사용자 생성
        self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
        self.user2.set_password("pass")
        self.user2.save()

        # 첫 번째 사용자로 로그인
        self.client.force_login(self.user1)  # 테스트 클라이언트를 사용하여 첫 번째 사용자를 강제 로그인 상태로
    
    def test_send_friend_request(self):  # 친구 요청을 보내는 기능을 테스트하는 메서드
        url = reverse('friendship-send')  # 'friendship-send'라는 이름의 URL을 역으로 찾기

        # 친구 요청을 보내는 POST 요청을 보냄 # 두 번째 사용자 ID를 포함하여 POST 요청을 보냄
        response = self.client.post(url, {'to_user_id': self.user2.id})  
        
        # 응답 상태 코드가 201인지 확인
        self.assertEqual(response.status_code, 201)
        
        # 응답 데이터에서 상태 메시지가 '요청 보냄'인지 확인
        self.assertEqual(response.data['message'], '요청 보냄')
        
        # 첫 번째 사용자와 두 번째 사용자 간의 친구 요청이 데이터베이스에 존재하는지 확인
        self.assertTrue(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())

    def test_send_friend_request_already_sent(self):  # 이미 친구 요청을 보낸 경우를 테스트
        Friendship.objects.create(from_user=self.user1, to_user=self.user2, status='pending')
        url = reverse('friendship-send')

        response = self.client.post(url, {'to_user_id': self.user2.id})  # 다시 친구 요청을 보냄
        
        # 응답 상태 코드가 400인지 확인
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 보낸 친구요청')

    def test_send_friend_request_already_accepted(self):  # 이미 수락된 친구 요청을 테스트
        Friendship.objects.create(from_user=self.user1, to_user=self.user2, status='accepted')  
        url = reverse('friendship-send')

        response = self.client.post(url, {'to_user_id': self.user2.id})  # 다시 친구 요청을 보냄
        
        # 응답 상태 코드가 400인지 확인
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 수락된 친구요청')

    def test_send_friend_request_declined(self):  # 거절된 친구 요청을 테스트
        Friendship.objects.create(from_user=self.user1, to_user=self.user2, status='declined')  # 기존 친구 요청 생성
        url = reverse('friendship-send')

        response = self.client.post(url, {'to_user_id': self.user2.id})  # 다시 친구 요청을 보냄
        
        # 응답 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '친구 재요청 완료')

    def test_send_friend_request_reverse_pending(self):
        # 역방향으로 pending 요청이 있는 경우
        Friendship.objects.create(from_user=self.user2, to_user=self.user1, status='pending')
        url = reverse('friendship-send')
        
        response = self.client.post(url, {'to_user_id': self.user2.id})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '상호 요청으로 친구가 되었습니다.')  # accepted로 바뀐 경우임에도 메시지는 수정 가능
        self.assertEqual(Friendship.objects.get(from_user=self.user2, to_user=self.user1).status, 'accepted')

    def test_send_friend_request_reverse_accepted(self):
        # 역방향으로 accepted 친구관계가 이미 있는 경우
        Friendship.objects.create(from_user=self.user2, to_user=self.user1, status='accepted')
        url = reverse('friendship-send')
        
        response = self.client.post(url, {'to_user_id': self.user2.id})
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 친구관계')

    def test_send_friend_request_reverse_declined(self):
        # 역방향으로 declined 요청이 있었던 경우
        Friendship.objects.create(from_user=self.user2, to_user=self.user1, status='declined')
        url = reverse('friendship-send')
        
        response = self.client.post(url, {'to_user_id': self.user2.id})
        
        self.assertEqual(response.status_code, 200)
        friendship = Friendship.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(friendship.status, 'pending')
        self.assertEqual(response.data['message'], '친구 요청 완료')

# class AcceptFriendRequestTest(APITestCase):
#     def setUp(self):
#         # 첫 번째 사용자 생성
#         self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')  # User 객체 생성
#         self.user1.set_password("pass")  # 비밀번호를 해시화하여 설정
#         self.user1.save()  # 사용자 객체를 데이터베이스에 저장

#         # 두 번째 사용자 생성
#         self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
#         self.user2.set_password("pass")
#         self.user2.save()

#         # 친구요청 생성
#         self.friendrequest = Friendship(from_user=self.user1,to_user=self.user2,status='pending')
#         self.friendrequest.save()

#         self.client.force_login(self.user2)  # 테스트 클라이언트를 사용하여 두 번째 사용자를 강제 로그인 상태로

#     def test_accept_friend_request(self):  # 친구 요청 수락 기능을 테스트하는 메서드
#         url = reverse('friendship-accept')  # 'friendship-accept'라는 이름의 URL을 역으로 찾기

#         # 친구 요청을 수락하는 POST 요청을 보냄
#         response = self.client.post(url, {'friendship_id': self.friendrequest.id}) # friendrequest.id를 포함하여 POST 요청을 보냄
        
#         # 응답 상태 코드가 200인지 확인
#         self.assertEqual(response.status_code, 200)
        
#         # 응답 데이터에서 상태 메시지가 '친구 요청 수락'인지 확인
#         self.assertEqual(response.data['status'], '친구 요청 수락')
        
#         # 친구 요청이 수락이 데이터베이스에 반영됐는지 확인        
#         self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).status,'accepted')