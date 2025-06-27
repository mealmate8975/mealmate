'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

chatroom_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .chatroom_service import ChatRoomService, ChatRoomQueryService, ChatRoomInvitationService
from .serializers import ChatRoomSerializer
from schedules.models import Schedules
from schedules.serializers import ScheduleSerializer


class CheckParticipantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chatroom_id):
        user = request.user
        result = ChatRoomService.check_participant(chatroom_id, user)

        if not result['exists']:
            return Response({'error': 'ChatRoom not found'}, status=status.HTTP_404_NOT_FOUND)

        if result['is_participant']:
            return Response({'allowed': True})
        else:
            return Response({'allowed': False}, status=status.HTTP_403_FORBIDDEN)


class ConfirmedChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        time_confirmed_excluding_ongoing_chatrooms = ChatRoomQueryService.get_time_confirmed_chatrooms_excluding_ongoing(user)
        serializer = ChatRoomSerializer(time_confirmed_excluding_ongoing_chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnconfirmedChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        unconfirmed_chatrooms = ChatRoomQueryService.get_time_unconfirmed_chatrooms(user)
        serializer = ChatRoomSerializer(unconfirmed_chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OnGoingChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        ongoing_chatrooms = ChatRoomQueryService.get_ongoing_chatroom(user)
        serializer = ChatRoomSerializer(ongoing_chatrooms)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSchedulesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        schedules = ChatRoomQueryService.get_user_schedules(user)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InviteFriendForHostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,chatroom_id,target_user_id):
        host = request.user
        success, message = ChatRoomInvitationService.invite_friend_for_host(host,chatroom_id,target_user_id)
        if not success:
            return Response({"detail": message}, status=400)
        return Response(status=201)
