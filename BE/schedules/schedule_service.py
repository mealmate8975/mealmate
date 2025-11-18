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
    
    # @staticmethod
    # def get_schedule(pk, user):
    #     '''

    #     '''
    #     schedule = get_object_or_404(Schedules, pk=pk, created_by=user)
    #     return ScheduleSerializer(schedule).data   

    @staticmethod
    def get_participant_user_ids(schedule_id,host): 
        '''
        약속 참가자들의 id 리스트를 반환하는 함수 (participant = host + guest)
        '''

        target_schedule = get_object_or_404(Schedules,pk=schedule_id)

        host_id = host.id

        if host_id != target_schedule.created_by.id: # host.id가 pk로 찾은 스케줄의 생성자의 id와 일치하는지 확인
            raise PermissionDenied("해당 스케줄에 대한 권한이 없습니다.")

        guest_id_list = list(Participants.objects.filter(schedule=target_schedule).values_list("participant_id", flat=True).distinct())
        participant_id_list = guest_id_list + [host_id]

        return participant_id_list

    @staticmethod
    def get_related_schedule_by_user_id(schedule_id,host):
        '''
        참가자들이 관련된 모든 스케줄 반환 
        '''

        participant_id_list = ScheduleQueryService.get_participant_user_ids(schedule_id,host)

        # 스케줄 참여자로 스케줄 찾기
        schedule_id_queryset_from_Participants = Participants.objects.filter(
            participant__in=participant_id_list
        ).values_list("schedule", flat=True).distinct()

        # 스케줄 생성자로 스케줄 찾기
        # (호스트의 id + 게스트들의 id)로 schedules 테이블에서 생성자로 스케줄 id 추출
        schedule_id_queryset_from_Schedules = Schedules.objects.filter(
            created_by__in=participant_id_list
        ).values_list("schedule_id", flat=True).distinct()

        combined_schedule_ids = set(chain(schedule_id_queryset_from_Participants, schedule_id_queryset_from_Schedules))
        # itertools.chain 객체이며, 단순한 lazy iterator

        return combined_schedule_ids

    @staticmethod
    def check_conflicting_schedule(schedule_id,new_schedule_start,new_schedule_end,host):
        '''
        새로운 스케줄과 겹치는 스케줄이 있는지 확인하는 메서드
        '''
        # 1. schedule_id로 약속의 참가자 모두 찾기
        participant_id_list = ScheduleQueryService.get_participant_user_ids(schedule_id,host)

        # 2. participant_id_list로 관련된 약속 모두 찾기
        
        
        # related_schedule_id_set = ScheduleQueryService.get_related_schedule_ids_by_user_ids(schedule_pk)

        if True:
            return True
        
        return False

class ScheduleTimeService:
    @staticmethod
    def update_schedule_time_if_available(schedule_id,user,new_schedule_start,new_schedule_end):
        '''
         0. 요청하는 사용자가 호스트인지 확인
         1. 새로 설정할 시작/종료 시간의 유효성 검증
         2. 새로운 약속 시간과 겹치는 기존 약속이 있는지 검사
        '''
        # 0. 요청하는 사용자가 호스트인지 확인
        target_schedule = get_object_or_404(Schedules,schedule_id= schedule_id)
        if user != target_schedule.created_by:
            raise PermissionDenied("해당 약속의 호스트만 시간을 수정할 수 있습니다.")

        # 1. 새로 설정할 시작/종료 시간의 유효성 검증
        serializer = ScheduleSerializer(data={"schedule_start": new_schedule_start, "schedule_end": new_schedule_end}, partial=True)
        serializer.is_valid(raise_exception=True)

        new_schedule_start = serializer.validated_data["schedule_start"]
        new_schedule_end = serializer.validated_data["schedule_end"]

        # 2. 새로운 약속 시간과 겹치는 기존 약속이 있는지 검사
        if ScheduleQueryService.check_conflicting_schedule(schedule_id,new_schedule_start,new_schedule_end): # 겹치는 약속이 있을 경우 True
            raise ValidationError("기존 약속과 충돌하는 시간대입니다.")

        data = {
            "schedule_start": new_schedule_start,
            "schedule_end": new_schedule_end,
        }

        return ScheduleCommandService.update_schedule(schedule_id,user,data)
