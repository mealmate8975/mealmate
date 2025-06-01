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
from .schedule_service import ScheduleService

"""pk값이 필요하지 않은 뷰입니다. => 스케줄 생성, 전체 조회"""
class ScheduleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = ScheduleService.list_schedules(request.user)
        return Response(data)

    def post(self, request):
        try:
            data = ScheduleService.create_schedule(request.data, request.user)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
"""pk 값이 필요한 뷰입니다. => 단일 조회, 삭제, 수정"""
class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            data = ScheduleService.get_schedule(pk, request.user)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        try:
            data = ScheduleService.update_schedule(pk, request.user, request.data)
            return Response(data, status=status.HTTP_206_PARTIAL_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            ScheduleService.delete_schedule(pk, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)