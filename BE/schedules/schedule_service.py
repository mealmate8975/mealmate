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
from django.utils import timezone

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

    # participant = host + guest
    # (호스트의 id + 게스트들의 id) 추출
    @staticmethod
    def get_participant_user_ids(pk,user): # 해당 스케줄의 pk와 request.user(생성자이자 호스트)를 통해 스케줄 호스트와 게스트들의 id를 찾아서 리턴하는 함수
        target_schedule = get_object_or_404(Schedules,pk=pk)

        if user.id != target_schedule.created_by.id: # user.id가 pk로 찾은 스케줄의 생성자 id와 일치하는지 확인하는 로직
            raise PermissionDenied("해당 스케줄에 대한 권한이 없습니다.")

        guest_id_list = list(Participants.objects.filter(schedule=target_schedule).values_list("participants_id", flat=True).distinct())
        participant_id_list = guest_id_list + [user.id]

        return participant_id_list

    @staticmethod
    def get_related_schedule_ids_by_user_ids(pk, user):
        participant_id_list = ScheduleService.get_participant_user_ids(pk, user)

        # 스케줄 참여자로 스케줄 찾기
        # (호스트의 id + 게스트들의 id)로 participants 테이블에서 스케줄 id 추출(중복제거)
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
    # 데이터가 많을 때 성능 저하를 방지하기 위해서 리스트를 최대한 적게 사용

    # 스케줄 id로 스케줄 테이블에서 해당하는 달에 속해있는 약속들 찾기
    def get_schedules_in_month_range(pk, user,new_schedule_start,new_schedule_end):        
        related_schedule_id_set = ScheduleService.get_related_schedule_ids_by_user_ids(pk,user)
        new_schedule_start_month = new_schedule_start.month
        new_schedule_end_month = new_schedule_end.month

        new_schedule_month_range = range(new_schedule_start_month,new_schedule_end_month+1)
        schedules_in_month_range = Schedules.objects.filter(schedule_id__in=related_schedule_id_set).filter(Q(schedule_start__month__in=new_schedule_month_range) | Q(schedule_end__month__in=new_schedule_month_range)).distinct()
        
        return schedules_in_month_range
    
    # 모두가 가능한 시간대 고르기
    def select_available_time(pk, user,new_schedule_start,new_schedule_end):
        if new_schedule_end < new_schedule_start:
            raise ValidationError("시작 날짜가 끝나는 날짜 보다 늦습니다.")

        schedules_in_month_range = ScheduleService.get_schedules_in_month_range(pk, user,new_schedule_start,new_schedule_end)
        # conflicting_time_queryset을 프론트로 보내줘서 새로운 스케줄의 시작과 끝 시간을 선택할 때 시각적으로 표현해줘야함

        # 기존 약속과 충돌하는 새로운 약속일 경우 에러 발생시키기
        if schedules_in_month_range.filter(schedule_end__gte=new_schedule_start,schedule_start__lte=new_schedule_end).exists():
            raise ValidationError("기존 약속과 충돌하는 새로운 약속입니다.")
            
        data = {
            "schedule_start": new_schedule_start,
            "schedule_end": new_schedule_end,
        }

        return ScheduleService.update_schedule(pk, user, data)
    
    # schedule update와 create에서 start < end 검증 로직 있는지 확인하기 