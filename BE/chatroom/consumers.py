'''
웹소켓 연결에서 요청을 받아 처리하는 핸들러 역할

일반 HTTP 요청에서는 views.py가 요청을 처리하듯이
웹소켓 요청에서는 consumers.py의 Consumer가 처리
'''

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from schedules.models import Schedules  # 지연 import
        from participants.models import Participants  # 지연 import
        from django.utils.functional import LazyObject

        self.schedule_id = self.scope['url_route']['kwargs']['schedule_id']
        user = self.scope['user']

        # LazyObject 풀어주기
        if isinstance(user, LazyObject):
            user = user._wrapped

        try:
            self.chatroom = await self.get_chatroom(self.schedule_id)
        except ObjectDoesNotExist:
            await self.close()
            return

        is_participant = await self.is_user_participant(user, self.chatroom)
        if not is_participant:
            await self.close()
            return

        self.room_group_name = f'chat_{self.schedule_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send_chat_history()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = data.get('sender', 'anonymous')

        self.save_message_to_mongo(self.schedule_id, sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    @database_sync_to_async
    def get_chatroom(self, schedule_id):
        from schedules.models import Schedules
        return Schedules.objects.get(id=schedule_id)

    @database_sync_to_async
    def is_user_participant(self, user, schedule):
        from participants.models import Participants
        return Participants.objects.filter(schedule=schedule, user=user).exists()

    def save_message_to_mongo(self, schedule_id, sender, message):
        collection = settings.MESSAGES_COLLECTION
        collection.insert_one({
            'schedule_id': schedule_id,
            'sender': sender,
            'message': message,
            'timestamp' : timezone.now(),
        })

    async def send_chat_history(self):
        collection = settings.MESSAGES_COLLECTION
        messages = collection.find({'schedule_id': self.schedule_id}).sort('_id', -1).limit(50)

        for msg in reversed(list(messages)):
            await self.send(text_data=json.dumps({
                'sender': msg['sender'],
                'message': msg['message'],
                'timestamp': msg.get('timestamp')
            }))