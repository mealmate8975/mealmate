'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

chatroom_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''

from django.shortcuts import render
from .models import ChatRoom, ChatParticipant
from schedules.models import Schedules

# from friendships.models import Friendship

class ChatRoomQueryService:
    @staticmethod
    def get_user_schedules(user):
        '''
        로그인한 유저가 속해있는 채팅방에 대응되는 스케줄 찾기
        '''
        chatroom_ids = ChatParticipant.objects.filter(user=user).values_list('chatroom', flat=True)
        schedule_queryset = Schedules.objects.filter(schedule_id__in=chatroom_ids)
        return schedule_queryset

    @staticmethod
    def get_confirmed_chatrooms(user):
        '''
        확정된 시작 시간을 가진 채팅방
        '''
        schedule_queryset = ChatRoomQueryService.get_user_schedules(user)
        confirmed_schedule_ids = schedule_queryset.filter(schedule_start__isnull=False).values_list('schedule_id', flat=True)
        confirmed_chatrooms = ChatRoom.objects.filter(schedule__schedule_id__in=confirmed_schedule_ids)
        return confirmed_chatrooms

    @staticmethod
    def get_unconfirmed_chatrooms(user):
        '''
        확정되지 않은 시작 시간을 가진 채팅방
        '''
        schedule_queryset = ChatRoomQueryService.get_user_schedules(user)
        unconfirmed_schedule_ids = schedule_queryset.filter(schedule_start__isnull=True).values_list('schedule_id', flat=True)
        unconfirmed_chatrooms = ChatRoom.objects.filter(schedule__schedule_id__in=unconfirmed_schedule_ids)
        return unconfirmed_chatrooms
    
class ChatRoomService:
    @staticmethod
    def check_participant(chatroom_id, user):
        """
        해당 채팅방에 사용자가 참가자인지 확인
        """
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return {'exists': False, 'is_participant': False}

        is_participant = ChatParticipant.objects.filter(chatroom=chatroom, user=user).exists()

        return {'exists': True, 'is_participant': is_participant}

class ChatRoomInvitationService:
    '''
    호스트와 게스트 모두 채팅방에 친구를 초대할 수 있음 (단, 게스트는 호스트의 승인 있을 경우에만 초대 가능)
    '''
    def invite_friends_for_host(chatroom_id,host,data):
        
        """
        호스트가 친구를 채팅방에 초대합니다.

        이미 초대된 친구인지 확인하는 로직 필요
        """
        pass
    
    def invite_friends_for_guest(chatroom_id,guest,data):
        """
        게스트가 자신의 친구에게 초대를 보내기 위해서 호스트의 승인을 기다립니다. 
        
        이미 초대된 친구인지 확인하는 로직 필요
        """
        pass

    def approve_invitation():
        """
        호스트가 게스트의 친구 초대를 허락하고 초대가 게스트의 친구에게 전달됩니다.
        """
        pass    
    
    def accept_invitation(chatroom_id):
        """
        초대 받은 친구가 초대를 수락합니다.

        초대를 수락하면
        participants 테이블과 chatroomparticipant 테이블에 id 추가
        """
        pass
