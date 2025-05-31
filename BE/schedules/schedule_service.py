'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

schedule_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''

from .models import Schedules
from .serializers import ScheduleSerializer
from django.shortcuts import get_object_or_404

class ScheduleService:
    @staticmethod
    def list_schedules(user):
        schedules = Schedules.objects.filter(created_by=user)
        return ScheduleSerializer(schedules, many=True).data

    @staticmethod
    def create_schedule(data, user):
        serializer = ScheduleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user)
        return serializer.data

    @staticmethod
    def get_schedule(pk, user):
        schedule = get_object_or_404(Schedules, pk=pk, created_by=user)
        return ScheduleSerializer(schedule).data

    @staticmethod
    def update_schedule(pk, user, data):
        schedule = get_object_or_404(Schedules, pk=pk, created_by=user)
        serializer = ScheduleSerializer(schedule, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @staticmethod
    def delete_schedule(pk, user):
        schedule = get_object_or_404(Schedules, pk=pk, created_by=user)
        schedule.delete()

    from django.utils import timezone
    from datetime import timedelta
    from participants.models import Participants

    # (호스트의 id + 게스트들의 id) 추출
    @staticmethod
    def get_all_related_user_ids(pk,user): # 해당 스케줄의 pk와 request.user(생성자이자 호스트)를 통해 스케줄 호스트와 게스트들의 id를 찾아서 리턴하는 함수
        target_schedule = get_object_or_404(Schedules,pk=pk)
        if user.id == target_schedule.created_by.id: # user가 pk로 찾은 스케줄의 생성자와 일치하는지 확인하는 로직
            participant_id_list = Participants.objects.filter(schedule = target_schedule.id).value_list("participants",flat=True)
            # paticipants 테이블에서 스케줄 pk가 일치하는 참가자 id 모두 가져오기(중복없이) + user id

    # 참여자로 스케줄 찾기
    # (호스트의 id + 게스트들의 id)로 participants 테이블에서 스케줄 id 추출(중복제거)

    # 생성자로 스케줄 찾기
    # (호스트의 id + 게스트들의 id)로 schedules 테이블에서 생성자로 스케줄 id 추출

    # 스케줄 id 중복제거하기

    # 스케줄 id로 스케줄 테이블에서 약속 시작과 끝 정보 취합을 통해 모두가 가능한 시간 산출해내기
