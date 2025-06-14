import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import ChatRoom  # <- 여기 지연 import 유지

        self.room_id = self.scope['url_route']['kwargs']['room_id']

        try:
            self.chatroom = await self.get_chatroom(self.room_id)
        except ObjectDoesNotExist:
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

    async def get_chatroom(self, room_id):
        from .models import ChatRoom  # <-- 여기에도 지연 import
        return await ChatRoom.objects.aget(id=room_id)

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