from rest_framework.test import APITestCase
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from django.contrib.auth import get_user_model
from django.utils import timezone


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

class GetChatroomTest(ChatRoomTestBase):
    def test_get_time_confirmed_chatrooms(self):

        now = timezone.now()
        # 호스트 : user1, 게스트 : user2        
        schedule_instance1 = Schedules.objects.create(created_by=self.user1,schedule_start=now,with_chatroom=True)
        chatroom_instance1 = ChatRoom.objects.create(schedule=schedule_instance1,)
        ChatParticipant.objects.create(chatroom=chatroom_instance1,user=self.user1)
        ChatParticipant.objects.create(chatroom=chatroom_instance1,user=self.user2)

        # 호스트 : user3, 게스트 : user1
        schedule_instance2 = Schedules.objects.create(created_by=self.user3,schedule_start=now,with_chatroom=True)
        chatroom_instance2 = ChatRoom.objects.create(schedule=schedule_instance2)
        ChatParticipant.objects.create(chatroom=chatroom_instance2,user=self.user3)
        ChatParticipant.objects.create(chatroom=chatroom_instance2,user=self.user1)

        # 호스트 : user2, 게스트 : user3
        schedule_instance3 = Schedules.objects.create(created_by=self.user2,with_chatroom=True)
        chatroom_instance3 = ChatRoom.objects.create(schedule=schedule_instance3)
        ChatParticipant.objects.create(chatroom=chatroom_instance3,user=self.user2)
        ChatParticipant.objects.create(chatroom=chatroom_instance3,user=self.user3)

        url = reverse('chatroom:confirmed_chatrooms')
        response = self.client.get(url)
        response_data = response.json()
        print(response_data)
        self.assertEqual(len(response_data),2)
        chatroom_ids = [chatroom['id'] for chatroom in response_data]
        self.assertNotIn(chatroom_instance3.id, chatroom_ids)
        self.assertEqual(response.status_code, 200)