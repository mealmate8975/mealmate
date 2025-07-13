from django.shortcuts import render, get_object_or_404
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from schedules.models import Schedules

from .map_service import RealTimeLocationService

class UpdateRealTimeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request):
        # 위도/경도 타입 및 범위 검증
        try:
            lat = float(request.data.get("latitude"))
            lng = float(request.data.get("longitude"))
        except (ValueError, TypeError):
            return Response({"detail": "위도와 경도는 숫자여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return Response({"detail": "위도는 -90~90, 경도는 -180~180 사이여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 위도, 경도가 유효한 경우 서비스 호출
        msg = RealTimeLocationService.update_real_time_location(request.user, lat, lng)

        if msg == "Coords created successfully.":
            return Response({"message": msg},status=201)
        
        if msg == "Coords updated successfully.":
            return Response({"message": msg},status=200)

class SendUpdatedCoordinatesView(APIView):
    pass