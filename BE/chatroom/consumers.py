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

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import ChatRoom, ChatParticipant  # 지연 import
        from django.utils.functional import LazyObject

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user = self.scope['user']

        # LazyObject 풀어주기
        if isinstance(user, LazyObject):
            user = user._wrapped

        try:
            self.chatroom = await self.get_chatroom(self.room_id)
        except ObjectDoesNotExist:
            await self.close()
            return

        is_participant = await self.is_user_participant(user, self.chatroom)
        if not is_participant:
            await self.close()
            return

        self.room_group_name = f'chat_{self.room_id}'

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

        self.save_message_to_mongo(self.room_id, sender, message)

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
    def get_chatroom(self, room_id):
        from .models import ChatRoom
        return ChatRoom.objects.get(id=room_id)

    @database_sync_to_async
    def is_user_participant(self, user, chatroom):
        from .models import ChatParticipant
        return ChatParticipant.objects.filter(chatroom=chatroom, user=user).exists()

    def save_message_to_mongo(self, room_id, sender, message):
        collection = settings.MESSAGES_COLLECTION
        collection.insert_one({
            'room_id': room_id,
            'sender': sender,
            'message': message,
        })

    async def send_chat_history(self):
        collection = settings.MESSAGES_COLLECTION
        messages = collection.find({'room_id': self.room_id}).sort('_id', -1).limit(50)

        for msg in reversed(list(messages)):
            await self.send(text_data=json.dumps({
                'sender': msg['sender'],
                'message': msg['message'],
            }))