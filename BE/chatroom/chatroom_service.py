'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

chatroom_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''

from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from friendships.views import FriendRequestService
from django.contrib.auth import get_user_model

from .models import Invitation,InvitationBlock
from schedules.models import Schedules
from accounts.models import UserBlock
from friendships.models import Friendship
from participants.models import Participants

User = get_user_model()

class ChatRoomQueryService:
    @staticmethod
    def get_user_schedules(user):
        '''
        로그인한 유저가 속해있는 채팅방에 대응되는 스케줄 찾기
        '''
        chatroom_ids = Participants.objects.filter(participant=user).values_list('schedule', flat=True)
        schedule_queryset = Schedules.objects.filter(schedule_id__in=chatroom_ids)
        return schedule_queryset
    
    '''
    schedule_start의 null 여부로 confirmed_chatrooms와 unconfirmed_chatrooms로 나눈다
    '''

    @staticmethod
    def get_time_confirmed_chatrooms(user):
        '''
        확정된 시작 시간을 가진 채팅방 가져오기
        '''
        schedule_queryset = ChatRoomQueryService.get_user_schedules(user)
        time_confirmed_schedule_ids = schedule_queryset.filter(schedule_start__isnull=False).values_list('schedule_id', flat=True)
        time_confirmed_chatrooms = Schedules.objects.filter(schedule_id__in=time_confirmed_schedule_ids)
        return time_confirmed_chatrooms

    @staticmethod
    def get_time_unconfirmed_chatrooms(user):
        '''
        확정되지 않은 시작 시간을 가진 채팅방 가져오기
        '''
        schedule_queryset = ChatRoomQueryService.get_user_schedules(user)
        time_unconfirmed_schedule_ids = schedule_queryset.filter(schedule_start__isnull=True).values_list('schedule_id', flat=True)
        time_unconfirmed_chatrooms = Schedules.objects.filter(schedule_id__in=time_unconfirmed_schedule_ids)
        return time_unconfirmed_chatrooms

    @staticmethod
    def get_ongoing_chatroom(user):
        """
        확정된 시작 시간을 가진 채팅방 중 진행중인 채팅방 가져오기
        """
        time_confirmed_chatrooms = ChatRoomQueryService.get_time_confirmed_chatrooms(user)
        ongoing_chatrooms = time_confirmed_chatrooms.filter(schedule_start__lt=timezone.now()).exclude(schedule_end__lte=timezone.now())
        latest_chatroom = ongoing_chatrooms.order_by('-schedule_start').first()
        return latest_chatroom
       
    @staticmethod
    def get_time_confirmed_chatrooms_excluding_ongoing(user):
        """
        get_time_confirmed_chatrooms - get_ongoing_chatroom = result
        """
        time_confirmed = ChatRoomQueryService.get_time_confirmed_chatrooms(user)

        # 진행 중인 것 중 최신 하나만 찾아냄
        ongoing = time_confirmed.filter(
            schedule_start__lt=timezone.now(),
            schedule_end__gt=timezone.now(),
        ).order_by('-schedule_start')

        latest_ongoing = ongoing.first()
        result = time_confirmed.exclude(pk=latest_ongoing.pk if latest_ongoing else None)
        return result

class ChatRoomService:
    @staticmethod
    def check_participant(chatroom_id, user):
        """
        해당 채팅방에 사용자가 참가자인지 확인
        """
        try:
            chatroom = Schedules.objects.get(schedule_id=chatroom_id)
        except Schedules.DoesNotExist:
            return {'exists': False, 'is_participant': False}

        is_participant = Participants.objects.filter(schedule=chatroom, user=user).exists()

        return {'exists': True, 'is_participant': is_participant}


# 호스트와 게스트 모두 채팅방에 친구를 초대할 수 있음 (단, 게스트는 호스트의 승인 있을 경우에만 초대 가능)
class ChatRoomInvitationService:
    @staticmethod
    def check_invitable_state(chatroom_id,inviter_id,target_user_id):
        """
        초대 가능한 상태인지 확인하는 로직
        """        
        # 1. target user가 채팅방에 대한 초대 차단을 한 경우
        chatroom_blocked = InvitationBlock.objects.filter(blocking_user=target_user_id,blocked_schedule=chatroom_id).exists()
        if chatroom_blocked:
            return False, "This user has blocked invitations to this chatroom."
        
        # 2. inviter가 target user의 차단 목록에 있는 경우
        inviter_blocked = UserBlock.objects.filter(blocker=target_user_id,blocked_user=inviter_id).exists()
        if inviter_blocked:
            return False, "This user has blocked the inviter."
        
        # 3. 이미 보낸 초대가 존재하는 경우
        existing_invitation = Invitation.objects.filter(
        schedule=chatroom_id,
        from_user__id=inviter_id,
        to_user=target_user_id,
        status__in=['h_pending','pending','accepted']).exists()
        if existing_invitation:
            return False, "User has already been invited."
        
        # # 4. target user가 이미 채팅방에 있는 경우
        # already_in_chatroom = ChatParticipant.objects.filter(pk=chatroom_id,user=target_user_id).exists()
        # if already_in_chatroom:
        #     return False, "User is already in chatroom."
        # -> target user가 이미 채팅방에 있는 경우 ,accepted 조건에 해당되기 때문에 불필요
        
        return True, "Invitable"

    # 초대 불가한 경우
    # 1. target user가 채팅방에 대한 초대 차단을 한 경우
    # 2. inviter가 target user의 차단 목록에 있는 경우
    # 3. 초대가 이미 존재하는 경우 (status가 pending)
    # 4. 채팅방에 target user가 이미 존재하는 경우

    # 채팅방을 나갈 때 희망 시 채팅방 차단 로직 구현 필요

    @staticmethod
    def invite_friend_for_host(host,chatroom_id,target_user_id):
        """
        호스트가 친구를 채팅방에 초대합니다.
        """
        # 1단계 친구 관계인지 확인
        is_friend,friend_msg = FriendRequestService.check_friendship(host,target_user_id)
        if not is_friend:
            return False, friend_msg
        # 2단계 초대 가능한 상태인지 확인
        is_invitable,invite_msg = ChatRoomInvitationService.check_invitable_state(chatroom_id,host.id,target_user_id)
        if not is_invitable:
            return False, invite_msg
        
        chatroom = get_object_or_404(Schedules, schedule_id=chatroom_id)
        to_user = get_object_or_404(User,id=target_user_id)
        
        Invitation.objects.create(
            schedule=chatroom,
            from_user=host,
            to_user=to_user,
            status='pending')
        return True, "Invitation sent successfully."
    
    @staticmethod
    def invite_friend_for_guest(guest,chatroom_id,target_user_id):
        """
        게스트가 자신의 친구에게 초대를 보내기 위해서 호스트의 승인을 기다립니다. 
        """
        # 1단계 친구 관계인지 확인
        is_friend,friend_msg = FriendRequestService.check_friendship(guest,target_user_id)
        if not is_friend:
            return False, friend_msg
        # 2단계 초대 가능한 상태인지 확인
        is_invitable,invite_msg = ChatRoomInvitationService.check_invitable_state(chatroom_id,guest.id,target_user_id)
        if not is_invitable:
            return False, invite_msg
        
        chatroom = get_object_or_404(Schedules,pk=chatroom_id)
        to_user = get_object_or_404(User,pk=target_user_id)

        Invitation.objects.create(schedule=chatroom,from_user=guest,to_user=to_user,status='h_pending')
        return True,"Invitation request to host sent successfully."
    
    @staticmethod
    def check_is_host(user,schedule_instance):
        """
        로그인 중인 유저가 해당 스케줄의 호스트가 맞는지 확인
        """
        if schedule_instance.created_by == user:
            return True
        else:
            return False
    
    @staticmethod
    def approve_invitation(user,schedule_id,guest_id,target_user_id):
        """
        호스트가 게스트의 친구 초대를 허락(status : h_pending -> pending)
        """
        schedule_instance = get_object_or_404(Schedules,pk=schedule_id)

        # 로그인 중인 유저가 해당 스케줄의 호스트가 맞는지 확인
        is_host = ChatRoomInvitationService.check_is_host(user,schedule_instance)
        if is_host is False:
            return False, "Only the host can approve guest invitations."

        invitation_instance = get_object_or_404(
            Invitation,schedule=schedule_instance,
            from_user__id=guest_id,
            to_user__id=target_user_id,
            status='h_pending'
        )
        invitation_instance.status = 'pending'
        invitation_instance.save()
        return True, "Invitation approved successfully."
    @staticmethod
    def accept_invitation(invitation_id,user):
        """
        초대 받은 친구가 초대를 수락합니다.
        """
        invitation = get_object_or_404(Invitation,pk=invitation_id,status='pending')

        # 초대를 수락하면 Participants 테이블에 해당 레코드 추가
        with transaction.atomic():
            invitation.status = 'accepted'
            invitation.save()
            schedule_instance = invitation.schedule
            Participants.objects.create(schedule=schedule_instance,participant=user)
            return True, "Invitation accepted successfully."
    @staticmethod
    def reject_invitation(invitation_id):
        """
        초대 받은 친구가 초대를 거절합니다.
        """
        invitation = get_object_or_404(Invitation,pk=invitation_id,status='pending')
        invitation.status = 'rejected'
        invitation.save()
        return True, "Invitation rejected successfully."
        
    @staticmethod
    def get_received_invitations(user):
        return Invitation.objects.filter(to_user=user,status='pending')

    @staticmethod
    def get_invitations_awaiting_my_approval(user):
        schedule_list = Participants.objects.filter(is_host=True,participant=user).values_list('schedule')
        return Invitation.objects.filter(status='h_pending',schedule__schedule_id__in=schedule_list)