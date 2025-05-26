from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import ScheduleSerializer
from rest_framework.views import APIView
from rest_framework import status
from .models import Schedules

User = get_user_model()

"""pk값이 필요하지 않은 뷰입니다. => 스케줄 생성, 전체 조회"""
class ScheduleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedules = Schedules.objects.filter(created_by = request.user)
        serializer = ScheduleSerializer(schedules, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ScheduleSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(created_by = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
"""pk 값이 필요한 뷰입니다. => 단일 조회, 삭제, 수정"""
class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # 스케줄을 가져오는 함수입니다. 
    def get_object(self, pk, user):
        return get_object_or_404(Schedules, pk = pk, created_by = user)
    
    def get(self, request, pk):
        schedules = self.get_object(pk, request.user)
        serializer = ScheduleSerializer(schedules)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        schedules = self.get_object(pk, request.user)
        serializer = ScheduleSerializer(schedules, data = request.data, partial = True) # patch => 부분 수정이라 partial = True를 켜야함
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        schedule = self.get_object(pk, request.user)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)