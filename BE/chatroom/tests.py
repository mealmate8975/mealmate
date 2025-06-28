from rest_framework.test import APITestCase
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


from chatroom.models import ChatParticipant,ChatRoom,InvitationBlock
from schedules.models import Schedules
from friendships.models import Friendship
# from participants.models import Participants

from chatroom.chatroom_service import ChatRoomInvitationService

User = get_user_model()

class ChatRoomTestBase(APITestCase):
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

        self.client.force_login(self.user1)

        now = timezone.now()
        self.one_hour_before = now - timedelta(hours=1)
        self.one_hour_later = now + timedelta(hours=1)

        # confirmed schedule 
        # host : user1 / guest : user2
        self.schedule_confirmed1 = Schedules.objects.create(created_by=self.user1, schedule_start=self.one_hour_later, with_chatroom=True)
        self.chatroom_confirmed1 = ChatRoom.objects.create(schedule=self.schedule_confirmed1)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed1, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed1, user=self.user2)
        # host : user3 / guest : user1
        self.schedule_confirmed2 = Schedules.objects.create(created_by=self.user3, schedule_start=self.one_hour_later, with_chatroom=True)
        self.chatroom_confirmed2 = ChatRoom.objects.create(schedule=self.schedule_confirmed2)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed2, user=self.user3)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed2, user=self.user1)

        # unconfirmed schedule
        # host : user1 / guest : user2
        self.schedule_unconfirmed = Schedules.objects.create(created_by=self.user1, schedule_start=None, with_chatroom=True)
        self.chatroom_unconfirmed = ChatRoom.objects.create(schedule=self.schedule_unconfirmed)
        ChatParticipant.objects.create(chatroom=self.chatroom_unconfirmed, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_unconfirmed, user=self.user2)

class GetChatroomTest(ChatRoomTestBase):
    def test_ongoing(self):
        # ongoing schedule
        # host : user1 / guest : user2
        self.schedule_ongoing = Schedules.objects.create(created_by=self.user1,schedule_start=self.one_hour_before,schedule_end=self.one_hour_later,with_chatroom=True)
        self.chatroom_ongoing = ChatRoom.objects.create(schedule=self.schedule_ongoing)
        ChatParticipant.objects.create(chatroom=self.chatroom_ongoing, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_ongoing, user=self.user2)
        
        url = reverse('chatroom:ongoing')
        response = self.client.get(url)
        response_data = response.json()
        # print(response_data)
        chatroom_id = response_data['id']
        self.assertEqual(self.chatroom_ongoing.id,chatroom_id)
        self.assertEqual(response.status_code, 200)

    def test_confirmed_excluding_ongoing(self):
        # ongoing schedule
        # host : user1 / guest : user2
        self.schedule_ongoing = Schedules.objects.create(created_by=self.user1,schedule_start=self.one_hour_before,schedule_end=self.one_hour_later,with_chatroom=True)
        self.chatroom_ongoing = ChatRoom.objects.create(schedule=self.schedule_ongoing)
        ChatParticipant.objects.create(chatroom=self.chatroom_ongoing, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_ongoing, user=self.user2)

        url = reverse('chatroom:confirmed-ongoing')
        response = self.client.get(url)
        response_data = response.json()
        # print(response_data)
        self.assertEqual(len(response_data),2) # 3 - 1 = 2
        chatroom_ids = [chatroom['id'] for chatroom in response_data]
        self.assertNotIn(self.chatroom_ongoing.id, chatroom_ids)
        self.assertEqual(response.status_code, 200)
    
    def test_confirmed_excluding_None(self):
        url = reverse('chatroom:confirmed-ongoing')
        response = self.client.get(url)
        response_data = response.json()
        # print(response_data)
        self.assertEqual(len(response_data),2) # 2 - 0 = 0
        self.assertEqual(response.status_code, 200)

    def test_unconfirmed(self):
        url = reverse('chatroom:unconfirmed')
        response = self.client.get(url)
        response_data = response.json()
        # print(response_data)
        self.assertEqual(len(response_data),1)
        chatroom_ids = [chatroom['id'] for chatroom in response_data]
        self.assertIn(self.chatroom_unconfirmed.id, chatroom_ids)
        self.assertEqual(response.status_code, 200)

class ChatRoomInvitationTestBase(APITestCase):
    def setUp(self):
        self.user1 = User(email="user1@example.com", name="User One", nickname="user1", gender='0')
        self.user1.set_password("pass")
        self.user1.save()

        self.user2 = User(email="user2@example.com", name="User Two", nickname="user2", gender='1')
        self.user2.set_password("pass")
        self.user2.save()

        self.client.force_login(self.user1)

        self.schedule1 = Schedules.objects.create(created_by=self.user1, with_chatroom=True)
        self.chatroom1 = ChatRoom.objects.create(schedule=self.schedule1)
        ChatParticipant.objects.create(chatroom=self.chatroom1, user=self.user1)
        Friendship.objects.create(from_user=self.user1,to_user=self.user2,status="accepted")

class ChatRoomInvitationTest(ChatRoomInvitationTestBase):
    def test_invitable_when_chatroom_blocked(self):
        InvitationBlock.objects.create(blocking_user=self.user2,blocked_chatroom=self.chatroom1)
        is_invitable, msg = ChatRoomInvitationService.check_invitable_state(self.chatroom1.id,self.user1.id,self.user2.id)
        self.assertFalse(is_invitable)
        # self.assertEqual(msg,"This user has blocked invitations to this chatroom.")

    def test_invite_friend_for_host(self): 
        url = reverse('chatroom:invite_friend_for_host', args=[self.chatroom1.id, self.user2.id])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code,201)