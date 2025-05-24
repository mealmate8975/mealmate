from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from .models import Friendship
from accounts.models import UserBlock

User = get_user_model()

class FriendTestBase(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
        self.user2.set_password("pass")
        self.user2.save()

        self.client.force_login(self.user1)

    def create_friendship(self, from_user, to_user, status):
        return Friendship.objects.create(from_user=from_user, to_user=to_user, status=status)

class SendFriendRequestTest(FriendTestBase):
    # 존재하지 않는 유저에게 요청을 보냈을 때 실패
    def test_send_friend_request_to_nonexistent_user(self):
        url = reverse('send-friend-request')
        nonexistent_user_id = User.objects.latest('id').id + 1
        response = self.client.post(url,{'to_user_id':nonexistent_user_id})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], '해당 유저가 존재하지 않습니다.')

    def send_request(self, to_user):
        url = reverse('send-friend-request')
        return self.client.post(url, {'to_user_id': to_user.id})
    
    # 나를 차단한 유저에게 친구 요청을 보냈을 때 실패
    def test_send_friend_request_to_blocked_user(self):
        UserBlock.objects.create(blocker=self.user2, blocked_user=self.user1)
        url = reverse('send-friend-request')
        response = self.client.post(url,{'to_user_id':self.user2.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '나를 차단한 유저에게 친구 요청을 보낼 수 없습니다.')

    def test_send_friend_request(self):  # 친구 요청을 보내는 기능을 테스트하는 메서드
        response = self.send_request(self.user2)
        
        # 응답 상태 코드가 201인지 확인
        self.assertEqual(response.status_code, 201)
        
        # 응답 데이터에서 상태 메시지가 '요청 보냄'인지 확인
        self.assertEqual(response.data['message'], '요청 보냄')
        
        # 첫 번째 사용자와 두 번째 사용자 간의 친구 요청이 데이터베이스에 존재하는지 확인
        self.assertTrue(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())

    def test_send_friend_request_already_sent(self):  # 이미 친구 요청을 보낸 경우를 테스트
        self.create_friendship(self.user1, self.user2, 'pending')
        response = self.send_request(self.user2)  # 다시 친구 요청을 보냄
        
        # 응답 상태 코드가 400인지 확인
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 보낸 친구요청')

    def test_send_friend_request_already_accepted(self):  # 이미 수락된 친구 요청을 테스트
        self.create_friendship(self.user1, self.user2, 'accepted')  
        response = self.send_request(self.user2)  # 다시 친구 요청을 보냄
        
        # 응답 상태 코드가 400인지 확인
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 수락된 친구요청')

    def test_send_friend_request_declined(self):  # 거절된 친구 요청을 테스트
        self.create_friendship(self.user1, self.user2, 'declined')  # 기존 친구 요청 생성
        response = self.send_request(self.user2)  # 다시 친구 요청을 보냄
        
        # 응답 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '친구 재요청 완료')

    def test_send_friend_request_reverse_pending(self):
        # 역방향으로 pending 요청이 있는 경우
        self.create_friendship(self.user2, self.user1, 'pending')
        
        response = self.send_request(self.user2)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '상호 요청으로 친구가 되었습니다.')  # accepted로 바뀐 경우임에도 메시지는 수정 가능
        self.assertEqual(Friendship.objects.get(from_user=self.user2, to_user=self.user1).status, 'accepted')

    def test_send_friend_request_reverse_accepted(self):
        # 역방향으로 accepted 친구관계가 이미 있는 경우
        self.create_friendship(self.user2, self.user1, 'accepted')
        
        response = self.send_request(self.user2)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 친구관계')

    def test_send_friend_request_reverse_declined(self):
        # 역방향으로 declined 요청이 있었던 경우
        self.create_friendship(self.user2, self.user1, 'declined')
        
        response = self.send_request(self.user2)
        
        self.assertEqual(response.status_code, 200)
        friendship = Friendship.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(friendship.status, 'pending')
        self.assertEqual(response.data['message'], '친구 요청 완료')

class AcceptFriendRequestTest(FriendTestBase):
    def setUp(self):
        super().setUp()
        # 친구 요청 생성 (user2 -> user1)
        self.friendship = self.create_friendship(self.user2, self.user1, 'pending')

    def test_accept_friend_request(self):
        url = reverse('accept-friend-request')
        response = self.client.post(url, {'from_user_id': self.user2.id})

        # 응답 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '친구 요청 수락 완료')

        # 친구 요청 상태가 'accepted'로 변경되었는지 확인
        self.friendship.refresh_from_db()
        self.assertEqual(self.friendship.status, 'accepted')

    def test_accept_nonexistent_friend_request(self):
        url = reverse('accept-friend-request')
        nonexistent_id = max(User.objects.all().values_list('id', flat=True), default=0) + 1000
        response = self.client.post(url, {'from_user_id': nonexistent_id})  # 존재하지 않는 사용자 ID
        ''' 
        client는 APITestCase가 제공하는 인스턴스 변수
        따라서 메서드 안에서 self.client로 접근하는 게 자연스럽고 필수적 
        '''

        # 응답 상태 코드가 404인지 확인
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], '요청을 처리할 수 없습니다.')

    def test_accept_already_accepted_friend_request(self):
        self.friendship.status = 'accepted'
        self.friendship.save()

        url = reverse('accept-friend-request')
        response = self.client.post(url, {'from_user_id': self.user2.id})

        # 응답 상태 코드가 400인지 확인
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 처리된 친구 요청입니다.')

class DeclineFriendRequestTest(FriendTestBase):
    def setUp(self):
        super().setUp()
        # 친구 요청 생성 (user2 -> user1)
        self.friendship = self.create_friendship(self.user2, self.user1, 'pending')

    def test_decline_friend_request(self):
        url = reverse('decline-friend-request')
        response = self.client.post(url, {'from_user_id': self.user2.id})

        # 응답 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '친구 요청 거절 완료')

        # 친구 요청 상태가 'declined'로 변경되었는지 확인
        self.friendship.refresh_from_db()
        self.assertEqual(self.friendship.status, 'declined')

    def test_decline_nonexistent_friend_request(self):
        url = reverse('decline-friend-request')
        nonexistent_id = max(User.objects.all().values_list('id', flat=True), default=0) + 1000
        response = self.client.post(url, {'from_user_id': nonexistent_id})  # 존재하지 않는 사용자 ID
        ''' 
        client는 APITestCase가 제공하는 인스턴스 변수
        따라서 메서드 안에서 self.client로 접근하는 게 자연스럽고 필수적 
        '''

        # 응답 상태 코드가 404인지 확인
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], '요청을 처리할 수 없습니다.')

    def test_decline_already_declined_friend_request(self):
        self.friendship.status = 'declined'
        self.friendship.save()

        url = reverse('decline-friend-request')
        response = self.client.post(url, {'from_user_id': self.user2.id})

        # 응답 상태 코드가 400인지 확인
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '이미 처리된 친구 요청입니다.')

class CancelFriendRequest(FriendTestBase):
    def setUp(self):
        super().setUp() # user1 -> user2
        self.create_friendship(self.user1, self.user2, 'pending') # user1 -> user2 요청 상태

    # 상대가 수락 / 거절 하기 전 취소
    def test_cancel_pending_request(self): 
        url = reverse('cancel-friend-request')
        response = self.client.post(url, {'to_user_id': self.user2.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '친구요청이 취소되었습니다.')
        self.assertFalse(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        
class DeleteFriendTest(FriendTestBase):
    def setUp(self):
        super().setUp()
        self.create_friendship(self.user1, self.user2, 'accepted')

    def test_delete_friend(self):
        url = reverse('delete-friendship')
        response = self.client.post(url, {'to_user_id': self.user2.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], '친구 관계가 삭제되었습니다.')
        self.assertFalse(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertFalse(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).exists())
        