from .models import ChatRoom, ChatParticipant, Invitation, InvitationBlock
from rest_framework import serializers

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'schedule']
        read_only_fields = ['id', 'schedule']

class ChatParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatParticipant
        fields = ['id', 'chatroom', 'user', 'joined_at']
        read_only_fields = ['id', 'joined_at']

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            'id', 'chatroom', 'from_user', 'to_user',
            'status', 'invited_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'invited_at', 'updated_at']

class InvitationBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationBlock
        fields = [
            'id','blocking_user','blocked_chatroom'
        ]
        read_only_fields = ['id','blocking_user']