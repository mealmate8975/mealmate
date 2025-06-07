'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

views.py
클라이언트의 HTTP 요청을 받고, 
인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어

schedule_service.py
실제 비즈니스 로직을 수행하는 서비스 계층
'''

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .schedule_service import *
from django.utils.dateparse import parse_datetime

"""pk값이 필요하지 않은 뷰입니다. => 스케줄 생성, 전체 조회"""
class ScheduleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = ScheduleQueryService.list_schedules(request.user)
        return Response(data)

    def post(self, request):
        try:
            data = ScheduleCommandService.create_schedule(request.data, request.user)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
"""pk 값이 필요한 뷰입니다. => 단일 조회, 삭제, 수정"""
class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            data = ScheduleQueryService.get_schedule(pk, request.user)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        try:
            data = ScheduleCommandService.update_schedule(pk, request.user, request.data)
            return Response(data, status=status.HTTP_206_PARTIAL_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            ScheduleCommandService.delete_schedule(pk, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

class ScheduleAvailableTimesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        start_dt = parse_datetime(start)
        end_dt = parse_datetime(end)

        schedules = ScheduleQueryService.get_schedules_in_month_range(pk, request.user, start_dt, end_dt)

        response_data = [
            {
                "schedule_id": s.schedule_id,
                "name": s.schedule_name,
                "start": s.schedule_start.isoformat(),
                "end": s.schedule_end.isoformat(),
            }
            for s in schedules
        ]
        return Response({"schedules": response_data})

class ScheduleSelectAvailableTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            start = request.data.get("schedule_start")
            end = request.data.get("schedule_end")
            # 날짜 형식 파싱 필요 시 추가
            data = ScheduleTimeService.select_available_time(pk, request.user, start, end)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)