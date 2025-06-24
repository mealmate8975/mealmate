from rest_framework.test import APITestCase
from django.urls import reverse  # URL을 역으로 찾기 위한 함수
from django.contrib.auth import get_user_model

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

class GetTimeconfirmedChatroomsTest(ChatRoomTestBase):
    def test1(self):
        # 호스트 : user1, 게스트 : user2
        schedule_instance1 = Schedules.objects.create(created_by=self.user1,with_chatroom=True)
        chatroom_instance1 = ChatRoom.objects.create(schedule=schedule_instance1)
        ChatParticipant.objects.create(chatroom=chatroom_instance1,user=self.user1)
        ChatParticipant.objects.create(chatroom=chatroom_instance1,user=self.user2)

        # 호스트 : user3, 게스트 : user1
        schedule_instance2 = Schedules.objects.create(created_by=self.user3,with_chatroom=True)
        chatroom_instance2 = ChatRoom.objects.create(schedule=schedule_instance2)
        ChatParticipant.objects.create(chatroom=chatroom_instance2,user=self.user3)
        ChatParticipant.objects.create(chatroom=chatroom_instance2,user=self.user1)

        url = reverse('confirmed_chatrooms')
        