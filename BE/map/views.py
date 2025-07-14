from django.shortcuts import render, get_object_or_404
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from map.sse_state import set_latest_coords
from django.http import StreamingHttpResponse
from map.sse_state import get_latest_coords
import time

from schedules.models import Schedules

from .map_service import RealTimeLocationService

class UpdateRealTimeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request,schedule_id):
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

        # 좌표 저장 후 참여자 전체 좌표 업데이트
        latest_coords = json.loads(RealTimeLocationService.get_all_participants_coords(schedule_id=schedule_id))
        set_latest_coords(latest_coords)

        if msg == "Coords created successfully.":
            return Response({"message": msg},status=201)
        
        if msg == "Coords updated successfully.":
            return Response({"message": msg},status=200)

class SendUpdatedCoordinatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        def event_stream(): # 이 내부 함수는 스트리밍 응답을 위해 무한 루프를 돌며 데이터를 계속 보냄
            while True:
                coords = get_latest_coords()
                yield f"data : {json.dumps(coords)}\n\n"
                # SSE 형식으로 데이터를 전송
                # "data: ...\n\n" 형식은 SSE 프로토콜의 기본 구조
                # 클라이언트에서는 이 데이터를 onmessage 이벤트로 받게 됨
                # onmessage 이벤트 : SSE나 WebSocket 연결을 통해 서버로부터 받은 메시지를 클라이언트가 수신할 때 실행되는 이벤트 처리기
                time.sleep(2) # 2초마다 반복해서 데이터를 전송 (브로드캐스트 간격 조절용)
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        # Django의 StreamingHttpResponse를 사용하여 스트리밍 응답을 생성
        # content_type을 'text/event-stream'으로 설정해야 브라우저가 SSE로 인식함