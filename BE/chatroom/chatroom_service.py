'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

chatroom_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''

from django.shortcuts import render
# from accounts.models import CustomUser
from friendships.models import Friendship

'''
호스트와 게스트는 모두 초대 가능
단, 게스트는 호스트의 승인 있을 경우에만 초대 가능
'''

'''
Invitation 모델 생성 필요
'''

class ChatRoomService:
    
    def invite_friends_for_host(chatroom_id,host,data):
        """
        호스트가 친구를 채팅방에 초대합니다.

        이미 초대된 친구인지 확인하는 로직 필요
        """
        pass
    
    def invite_friends_for_guest(chatroom_id,guest,data):
        """
        게스트가 친구를 채팅방에 초대하고 호스트의 승인을 기다립니다.
        
        이미 초대된 친구인지 확인하는 로직 필요
        """
        pass

    def approve_invitation():
        """
        호스트가 게스트의 친구 초대를 허락합니다.
        """
        pass
    
    def accept_invitation(chatroom_id,friend):
        """
        초대 받은 친구가 초대를 수락합니다.
        """
        pass
