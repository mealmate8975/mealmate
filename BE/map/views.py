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

    def patch(self,request,latitude,longitude):
        # 위도/경도 타입 및 범위 검증
        try:
            lat = float(latitude)
            lng = float(longitude)
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
        

# def map_view(request):
#     schedule_id = request.GET.get("schedule_id")

#     # 1. schedule_id 없을 경우 폼만 보여줌
#     if not schedule_id:
#         return render(request, 'map/map_form.html')
    
#     # 2. 스케줄 조회
#     schedule = get_object_or_404(Schedules, schedule_id=schedule_id)
#     coord = schedule.schedule_condition or {} 
#     # schedule.schedule_condition이 None이면 coord는 {} 빈 딕셔너리를 할당받음
    
#     # 3. 좌표 추출 (예외 방지용 기본값 처리)
#     try:
#         coords = {
#             "lat": coord["latitude"],
#             "lng": coord["longitude"]
#         }
#     except KeyError:
#         coords = {
#             "lat": 37.5665,
#             "lng": 126.9780
#         }
#     return render(request, 'map/map.html', {
#     "coords": json.dumps(coords)
#     })