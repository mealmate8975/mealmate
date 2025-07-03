from rest_framework.test import APITestCase
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from chatroom.models import InvitationBlock,Invitation
from schedules.models import Schedules
from friendships.models import Friendship
from accounts.models import UserBlock
from participants.models import Participants

from chatroom.chatroom_service import ChatRoomInvitationService

User = get_user_model()

# 채팅방 테스트 기본 클래스
# class ChatRoomTestBase(APITestCase):
#     def setUp(self):
#         self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
#         self.user1.set_password("pass")
#         self.user1.save()

#         self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
#         self.user2.set_password("pass")
#         self.user2.save()

#         self.user3 = User(email="user3@example.com", name="User Three", nickname="user3", gender='0')
#         self.user3.set_password("pass")
#         self.user3.save()

#         self.client.force_login(self.user1)

#         now = timezone.now()
#         self.one_hour_before = now - timedelta(hours=1)
#         self.one_hour_later = now + timedelta(hours=1)

#         # confirmed schedule 
#         # host : user1 / guest : user2
#         self.schedule_confirmed1 = Schedules.objects.create(created_by=self.user1, schedule_start=self.one_hour_later, is_chatroom=True)
#         Participants.objects.create(schedule=self.schedule_confirmed1, participant=self.user1)
#         Participants.objects.create(schedule=self.schedule_confirmed1, participant=self.user2)

#         # host : user3 / guest : user1
#         self.schedule_confirmed2 = Schedules.objects.create(created_by=self.user3, schedule_start=self.one_hour_later, is_chatroom=True)
#         Participants.objects.create(schedule=self.schedule_confirmed2, participant=self.user3)
#         Participants.objects.create(schedule=self.schedule_confirmed2, participant=self.user1)

#         # unconfirmed schedule
#         # host : user1 / guest : user2
#         self.schedule_unconfirmed = Schedules.objects.create(created_by=self.user1, schedule_start=None, is_chatroom=True)
#         Participants.objects.create(schedule=self.schedule_unconfirmed, participant=self.user1)
#         Participants.objects.create(schedule=self.schedule_unconfirmed, participant=self.user2)

# # 채팅방 테스트 클래스
# class GetChatroomTest(ChatRoomTestBase):
#     # 현재 진행중인 채팅방 조회
#     def test_ongoing(self):
#         # ongoing schedule
#         # host : user1 / guest : user2
#         self.schedule_ongoing = Schedules.objects.create(created_by=self.user1,schedule_start=self.one_hour_before,schedule_end=self.one_hour_later,is_chatroom=True)
#         Participants.objects.create(schedule=self.schedule_ongoing, participant=self.user1)
#         Participants.objects.create(schedule=self.schedule_ongoing, participant=self.user2)
        
#         url = reverse('chatroom:ongoing')
#         response = self.client.get(url)
#         response_data = response.json()
#         # print(response_data)
#         chatroom_id = response_data['schedule_id']
#         self.assertEqual(self.schedule_ongoing.schedule_id,chatroom_id)
#         self.assertEqual(response.status_code, 200)

#     # 현재 진행중인 채팅방 제외하고 확정된 채팅방 조회
#     def test_confirmed_excluding_ongoing(self):
#         # ongoing schedule
#         # host : user1 / guest : user2
#         self.schedule_ongoing = Schedules.objects.create(created_by=self.user1,schedule_start=self.one_hour_before,schedule_end=self.one_hour_later,is_chatroom=True)
#         Participants.objects.create(schedule=self.schedule_ongoing, participant=self.user1)
#         Participants.objects.create(schedule=self.schedule_ongoing, participant=self.user2)

#         url = reverse('chatroom:confirmed-ongoing')
#         response = self.client.get(url)
#         response_data = response.json()
#         # print(response_data)
#         self.assertEqual(len(response_data),2) # 3 - 1 = 2
#         chatroom_ids = [chatroom['schedule_id'] for chatroom in response_data]
#         self.assertNotIn(self.schedule_ongoing.schedule_id, chatroom_ids)
#         self.assertEqual(response.status_code, 200)
    
#     # 확정된 채팅방 조회 (확정된 채팅방이 없는 경우)
#     def test_confirmed_excluding_None(self):
#         url = reverse('chatroom:confirmed-ongoing')
#         response = self.client.get(url)
#         response_data = response.json()
#         # print(response_data)
#         self.assertEqual(len(response_data),2) # 2 - 0 = 0
#         self.assertEqual(response.status_code, 200)

#     # 확정되지 않은 채팅방 조회
#     def test_unconfirmed(self):
#         url = reverse('chatroom:unconfirmed')
#         response = self.client.get(url)
#         response_data = response.json()
#         # print(response_data)
#         self.assertEqual(len(response_data),1)
#         chatroom_ids = [chatroom['schedule_id'] for chatroom in response_data]
#         self.assertIn(self.schedule_unconfirmed.schedule_id, chatroom_ids)
#         self.assertEqual(response.status_code, 200)

# 채팅방 초대 테스트 기본 클래스
class ChatRoomInvitationTestBase(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
        self.user2.set_password("pass")
        self.user2.save()

        self.user3 = User(email="user3@example.com", name="User Three", nickname="user3", gender='0')
        self.user3.set_password("pass")
        self.user3.save()

        self.schedule1 = Schedules.objects.create(created_by=self.user1, is_chatroom=True)
        Participants.objects.create(schedule=self.schedule1, participant=self.user1, is_host=True)
        Friendship.objects.create(from_user=self.user1,to_user=self.user2,status="accepted")

# 채팅방 초대 테스트 클래스
class ChatRoomInvitationTest(ChatRoomInvitationTestBase):
    # 채팅방 차단 상태일 때 초대 가능 여부 테스트
    # def test_invitable_when_chatroom_blocked(self):
    #     InvitationBlock.objects.create(blocking_user=self.user2,blocked_schedule=self.schedule1)
    #     is_invitable, msg = ChatRoomInvitationService.check_invitable_state(self.schedule1.schedule_id,self.user1.id,self.user2.id)
    #     self.assertFalse(is_invitable)
    #     self.assertEqual(msg,"This user has blocked invitations to this chatroom.")
    
    # # 초대자 차단 상태일 때 초대 가능 여부 테스트
    # def test_invitable_when_inviter_blocked(self):
    #     UserBlock.objects.create(blocker=self.user2,blocked_user=self.user1)
    #     is_invitable, msg = ChatRoomInvitationService.check_invitable_state(self.schedule1.schedule_id,self.user1.id,self.user2.id)
    #     self.assertFalse(is_invitable)
    #     self.assertEqual(msg,"This user has blocked the inviter.")
    
    # # 초대 대기 상태일 때 초대 가능 여부 테스트
    # def test_invitable_when_hpending(self):
    #     Invitation.objects.create(schedule=self.schedule1,from_user=self.user1,to_user=self.user2,status="h_pending")
    #     is_invitable, msg = ChatRoomInvitationService.check_invitable_state(self.schedule1.schedule_id,self.user1.id,self.user2.id)
    #     self.assertFalse(is_invitable)
    #     self.assertEqual(msg,"User has already been invited.")
    
    # # 초대 대기 상태일 때 초대 가능 여부 테스트
    # def test_invitable_when_pending(self):
    #     Invitation.objects.create(schedule=self.schedule1,from_user=self.user1,to_user=self.user2,status="pending")
    #     is_invitable, msg = ChatRoomInvitationService.check_invitable_state(self.schedule1.schedule_id,self.user1.id,self.user2.id)
    #     self.assertFalse(is_invitable)
    #     self.assertEqual(msg,"User has already been invited.")
    
    # # 초대 수락 상태일 때 초대 가능 여부 테스트
    # def test_invitable_when_accepted(self):
    #     Invitation.objects.create(schedule=self.schedule1,from_user=self.user1,to_user=self.user2,status="accepted")
    #     is_invitable, msg = ChatRoomInvitationService.check_invitable_state(self.schedule1.schedule_id,self.user1.id,self.user2.id)
    #     self.assertFalse(is_invitable)
    #     self.assertEqual(msg,"User has already been invited.")

    # # 채팅방 주인이 친구 초대 테스트
    # def test_invite_friend_for_host(self): 
    #     self.client.force_login(self.user1)

    #     url = reverse('chatroom:invite_friend_for_host', args=[self.schedule1.schedule_id, self.user2.id])
    #     response = self.client.post(url, {}, format="json")
    #     self.assertEqual(response.status_code,201)
    
    # # 채팅방 참여자가 친구 초대 테스트
    # def test_invite_friend_for_guest(self):
    #     self.client.force_login(self.user2)

    #     Participants.objects.create(schedule=self.schedule1, participant=self.user2)
    #     Friendship.objects.create(from_user=self.user2,to_user=self.user3,status="accepted")

    #     url = reverse('chatroom:invite_friend_for_guest',args=[self.schedule1.schedule_id,self.user3.id])
    #     response = self.client.post(url, {}, format="json")
    #     self.assertEqual(response.status_code,201)
    
    def test_approve_invitation(self):
        Friendship.objects.create(from_user=self.user2,to_user=self.user3,status="accepted")
        Invitation.objects.create(schedule=self.schedule1,from_user=self.user2,to_user=self.user3,status="h_pending")

        self.client.force_login(self.user1)

        url = reverse('chatroom:approve_invitation',args=[self.schedule1.schedule_id,self.user2.id,self.user3.id])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code,200)

    def test_accept_invitation(self):
        Friendship.objects.create(from_user=self.user2,to_user=self.user3,status="accepted")
        invitation_instance = Invitation.objects.create(schedule=self.schedule1,from_user=self.user2,to_user=self.user3,status="pending")

        self.client.force_login(self.user3)

        url = reverse('chatroom:accept_invitation',args=[invitation_instance.pk])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code,201)
    
    def test_reject_invitation(self):
        Friendship.objects.create(from_user=self.user2,to_user=self.user3,status="accepted")
        invitation_instance = Invitation.objects.create(schedule=self.schedule1,from_user=self.user2,to_user=self.user3,status="pending")

        self.client.force_login(self.user3)

        url = reverse('chatroom:reject_invitation',args=[invitation_instance.pk])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code,200)
    
    def test_내가받은초대리스트조회(self):
        Participants.objects.create(schedule=self.schedule1, participant=self.user2)
        Friendship.objects.create(from_user=self.user2,to_user=self.user3,status="accepted")
        Invitation.objects.create(schedule=self.schedule1,from_user=self.user1,to_user=self.user3,status='pending')
        Invitation.objects.create(schedule=self.schedule1,from_user=self.user2,to_user=self.user3,status='pending')

        self.client.force_login(self.user3)

        url = reverse('chatroom:내가받은초대리스트조회')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)