'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

schedule_service.py
스케줄 생성, 조회, 수정, 삭제에 대한 실제 비즈니스 로직을 수행하는 서비스 계층

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