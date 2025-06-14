from .models import ChatRoom, ChatParticipant, Invitation
from rest_framework import serializers

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = [
            '',
            ''
        ]
        # read_only_fields = ('',)

class ChatParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatParticipant
        fields = [
            '',
            ''
        ]
        # read_only_fields = ('',)

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            '',
            ''
        ]
        # read_only_fields = ('',)v
