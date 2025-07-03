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
from schedules.models import Schedules
from schedules.serializers import ScheduleSerializer
from .serializers import InvitationSerializer

# 채팅방 참여자 확인
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


# 확정된 채팅방 조회
class ConfirmedChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        time_confirmed_excluding_ongoing_chatrooms = ChatRoomQueryService.get_time_confirmed_chatrooms_excluding_ongoing(user)
        serializer = ScheduleSerializer(time_confirmed_excluding_ongoing_chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 확정되지 않은 채팅방 조회
class UnconfirmedChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        unconfirmed_chatrooms = ChatRoomQueryService.get_time_unconfirmed_chatrooms(user)
        serializer = ScheduleSerializer(unconfirmed_chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 현재 진행중인 채팅방 조회
class OnGoingChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        ongoing_chatrooms = ChatRoomQueryService.get_ongoing_chatroom(user)
        serializer = ScheduleSerializer(ongoing_chatrooms)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 유저 일정 조회
class UserSchedulesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        schedules = ChatRoomQueryService.get_user_schedules(user)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 채팅방 주인이 친구 초대
class InviteFriendForHostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,chatroom_id,target_user_id):
        host = request.user
        print(f"[DEBUG][VIEW] host={host.id}, chatroom_id={chatroom_id}, target_user_id={target_user_id}")

        success, message = ChatRoomInvitationService.invite_friend_for_host(host,chatroom_id,target_user_id)
        print(f"[DEBUG][VIEW] success={success}, message={message}")
        
        if not success:
            return Response({"detail": message}, status=400)
        return Response(status=201)

# 채팅방 참여자가 친구 초대
class InviteFriendForGuestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,chatroom_id,target_user_id):
        guest = request.user
        print(f"[DEBUG][VIEW] guest={guest.id}, chatroom_id={chatroom_id}, target_user_id={target_user_id}")

        success, message = ChatRoomInvitationService.invite_friend_for_guest(guest,chatroom_id,target_user_id)
        print(f"[DEBUG][VIEW] success={success}, message={message}")
        
        if not success:
            return Response({"detail": message}, status=400)
        return Response(status=201)

class ApproveInvitationView(APIView):
    """
    호스트가 게스트의 친구 초대를 허락하는 로직의 APIView
    """
    permission_classes = [IsAuthenticated]
    
    def post(self,request,schedule_id,guest_id,target_user_id):
        print(f"[DEBUG][VIEW] schedule_id={schedule_id}, guest_id={guest_id}, target_user_id={target_user_id}")

        success,message = ChatRoomInvitationService.approve_invitation(request.user,schedule_id,guest_id,target_user_id)
        print(f"[DEBUG][VIEW] success={success}, message={message}")

        if not success:
            return Response({"detail": message}, status=403) # 존재하지 않는 Schedule이나 Invitation이면 Django가 자동으로 404 리턴
        return Response(status=200)
    
class AcceptInvitationView(APIView):
    """
    초대를 허락하는 로직의 APIView
    """
    permission_classes = [IsAuthenticated]

    def post(self,request,invitation_id):
        print(f"[DEBUG][VIEW] invitation_id={invitation_id}")

        success,message = ChatRoomInvitationService.accept_invitation(invitation_id,request.user)
        print(f"[DEBUG][VIEW] success={success}, message={message}")

        if not success:
            return Response({"detail": message}, status=400)
        return Response(status=201)

class RejectInvitationView(APIView):
    """
    초대를 거절하는 로직의 APIView
    """
    permission_classes = [IsAuthenticated]

    def post(self,request,invitation_id):
        print(f"[DEBUG][VIEW] invitation_id={invitation_id}")

        success,message = ChatRoomInvitationService.reject_invitation(invitation_id)
        print(f"[DEBUG][VIEW] success={success}, message={message}")

        if not success:
            return Response({"detail": message}, status=400)
        return Response(status=200)

class 내가받은초대리스트조회View(APIView):
    """
    내가받은초대리스트조회 로직의 APIView
    """
    permission_classes = [IsAuthenticated]
    def get(self,request):
        내가받은초대리스트 = ChatRoomInvitationService.내가받은초대리스트조회(request.user)
        serializer = InvitationSerializer(내가받은초대리스트, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)