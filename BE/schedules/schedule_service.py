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
from participants.models import Participants
from rest_framework.exceptions import PermissionDenied
from itertools import chain
from rest_framework.exceptions import ValidationError
from django.db.models import Q

class ScheduleCommandService:
    @staticmethod
    def create_schedule(data, user):
        serializer = ScheduleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user)
        return serializer.data

    @staticmethod
    def update_schedule(schedule_id, user, data):
        schedule = get_object_or_404(Schedules, schedule_id=schedule_id, created_by=user)
        serializer = ScheduleSerializer(schedule, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @staticmethod
    def delete_schedule(pk, user):
        schedule = get_object_or_404(Schedules, pk=pk, created_by=user)
        schedule.delete()
    
class ScheduleQueryService:
    @staticmethod
    def list_schedules(user):
        schedules = Schedules.objects.filter(created_by=user)
        return ScheduleSerializer(schedules, many=True).data
    
    @staticmethod
    def get_participant_id_list(schedule_id): 
        '''
        약속의 참가자들 쿼리셋 반환
        '''
        target_schedule = get_object_or_404(Schedules,pk=schedule_id)

        participant_queryset= Participants.objects.filter(schedule=target_schedule).values_list("participant_id", flat=True).distinct()
        
        return participant_queryset

    @staticmethod
    def get_related_schedule_queryset(schedule_id):
        '''
        참가자들이 속해있는 모든 스케줄 쿼리셋 반환 
        '''
        participant_queryset = ScheduleQueryService.get_participant_id_list(schedule_id)

        schedule_id_queryset = Participants.objects.filter(
            participant__in=participant_queryset
        ).values_list("schedule", flat=True).distinct()

        return schedule_id_queryset

    @staticmethod
    def check_conflicting_schedule(schedule_id,new_schedule_start,new_schedule_end):
        '''
        새로운 스케줄 시간이
        같은 참여자 그룹이 속해 있는 '다른' 스케줄들과 겹치는지 여부를 반환

        반환:
            True  -> 하나 이상 충돌하는 스케줄 있음
            False -> 충돌 없음
        '''
        schedule_id_queryset = ScheduleQueryService.get_related_schedule_queryset(schedule_id)

        conflicting_schedules = Schedules.objects.filter(schedule_id__in=schedule_id_queryset).exclude(schedule_id=schedule_id).filter(
            Q(schedule_start__lt=new_schedule_end) & Q(schedule_end__gt=new_schedule_start)
        )

        return conflicting_schedules.exists()

class ScheduleTimeService:
    @staticmethod
    def update_schedule_time_if_available(user,schedule_id,new_schedule_start,new_schedule_end):
        '''
        스케줄 시간 업데이트

         1. 요청하는 사용자가 해당 스케줄의 호스트인지 확인
         2. 새로 설정할 시작/종료 시간의 유효성 검증
         3. 새로운 약속 시간과 겹치는 기존 약속이 있는지 검사
        '''
        # 1. 요청하는 사용자가 해당 스케줄의 호스트인지 확인

        target_schedule = get_object_or_404(Schedules, schedule_id = schedule_id) 
        
        if not Participants.objects.filter(
            schedule=target_schedule,
            participant=user,
            is_host=True
            ).exists():
            raise PermissionDenied("해당 약속의 호스트만 시간을 수정할 수 있습니다.")

        # 2. 새로 설정할 시작/종료 시간의 유효성 검증
        serializer = ScheduleSerializer(data={"schedule_start": new_schedule_start, "schedule_end": new_schedule_end}, partial=True)
        serializer.is_valid(raise_exception=True)

        new_schedule_start = serializer.validated_data["schedule_start"]
        new_schedule_end = serializer.validated_data["schedule_end"]

        # 3. 새로운 약속 시간과 겹치는 기존 약속이 있는지 검사
        if ScheduleQueryService.check_conflicting_schedule(schedule_id,new_schedule_start,new_schedule_end): # 겹치는 약속이 있을 경우 True
            raise ValidationError("기존 약속과 충돌하는 시간대입니다.")

        data = {
            "schedule_start": new_schedule_start,
            "schedule_end": new_schedule_end,
        }

        return ScheduleCommandService.update_schedule(schedule_id,user,data)
