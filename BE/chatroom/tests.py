from rest_framework.test import APITestCase
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


from chatroom.models import ChatParticipant,ChatRoom
from schedules.models import Schedules
# from participants.models import Participants

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
        one_hour_before = now - timedelta(hours=1)
        one_hour_later = now + timedelta(hours=1)

        # confirmed schedule 
        # host : user1 / guest : user2
        self.schedule_confirmed1 = Schedules.objects.create(created_by=self.user1, schedule_start=one_hour_later, with_chatroom=True)
        self.chatroom_confirmed1 = ChatRoom.objects.create(schedule=self.schedule_confirmed1)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed1, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed1, user=self.user2)
        # host : user3 / guest : user1
        self.schedule_confirmed2 = Schedules.objects.create(created_by=self.user3, schedule_start=one_hour_later, with_chatroom=True)
        self.chatroom_confirmed2 = ChatRoom.objects.create(schedule=self.schedule_confirmed2)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed2, user=self.user3)
        ChatParticipant.objects.create(chatroom=self.chatroom_confirmed2, user=self.user1)

        # unconfirmed schedule
        # host : user1 / guest : user2
        self.schedule_unconfirmed = Schedules.objects.create(created_by=self.user1, schedule_start=None, with_chatroom=True)
        self.chatroom_unconfirmed = ChatRoom.objects.create(schedule=self.schedule_unconfirmed)
        ChatParticipant.objects.create(chatroom=self.chatroom_unconfirmed, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_unconfirmed, user=self.user2)

        # ongoing schedule
        # host : user1 / guest : user2
        self.schedule_ongoing = Schedules.objects.create(created_by=self.user1,schedule_start=one_hour_before,schedule_end=one_hour_later,with_chatroom=True)
        self.chatroom_ongoing = ChatRoom.objects.create(schedule=self.schedule_ongoing)
        ChatParticipant.objects.create(chatroom=self.chatroom_ongoing, user=self.user1)
        ChatParticipant.objects.create(chatroom=self.chatroom_ongoing, user=self.user2)

class GetChatroomTest(ChatRoomTestBase):
    def test_get_time_confirmed_chatrooms(self):
        url = reverse('chatroom:confirmed_chatrooms')
        response = self.client.get(url)
        response_data = response.json()
        print(response_data)
        self.assertEqual(len(response_data),3)
        chatroom_ids = [chatroom['id'] for chatroom in response_data]
        self.assertNotIn(self.chatroom_unconfirmed.id, chatroom_ids)
        self.assertEqual(response.status_code, 200)

    def test_get_time_unconfirmed_chatrooms(self):
        url = reverse('chatroom:unconfirmed_chatrooms')
        response = self.client.get(url)
        response_data = response.json()
        print(response_data)
        self.assertEqual(len(response_data),1)
        chatroom_ids = [chatroom['id'] for chatroom in response_data]
        self.assertIn(self.chatroom_unconfirmed.id, chatroom_ids)
        self.assertEqual(response.status_code, 200)
    
    def test_get_ongoing_chatroom(self):
        url = reverse('chatroom:ongoing_chatrooms')
        response = self.client.get(url)
        response_data = response.json()
        print(response_data)
        chatroom_id = response_data['id']
        self.assertEqual(self.chatroom_ongoing.id,chatroom_id)
        self.assertEqual(response.status_code, 200)