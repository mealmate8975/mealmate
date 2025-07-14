'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

map_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''
from django.db import transaction
from django.shortcuts import get_object_or_404
import json

from .models import RealTimeLocation
from schedules.models import Schedules
from participants.models import Participants

class RealTimeLocationService:
    @staticmethod
    def update_real_time_location(user, latitude, longitude):
        with transaction.atomic():
            instance = RealTimeLocation.objects.filter(user=user).first()
            if instance:
                instance.latitude = latitude
                instance.longitude = longitude
                instance.save()
                return "Coords updated successfully."
            else:
                RealTimeLocation.objects.create(user=user, latitude=latitude, longitude=longitude)
                return "Coords created successfully."
            
    @staticmethod        
    def get_location_coords(schedule_id):
        # 약속 장소
        schedule = get_object_or_404(Schedules, schedule_id=schedule_id)
        coord = schedule.schedule_condition
        if not coord or "latitude" not in coord or "longitude" not in coord:
            return json.dumps({"lat": None, "lng": None})

        return json.dumps({
            "lat": coord["latitude"],
            "lng": coord["longitude"]
        })
    
    @staticmethod
    def get_participant_coords(user_id):
        # 약속 참가자의 실시간 위치
        real_time_location = get_object_or_404(RealTimeLocation,user_id=user_id)
        lat = real_time_location.latitude
        lng = real_time_location.longitude

        if lat is None or lng is None:
            return None  # 혹은 return {"user_id": user_id, "lat": None, "lng": None}

        return {
        "user_id": user_id,
        "lat": lat,
        "lng": lng
        }
    
    @staticmethod
    def get_all_participants_coords(schedule_id):
        # 약속 모든 참가자의 실시간 위치
        user_id_list = Participants.objects.filter(schedule_id=schedule_id).values_list('participant__id', flat=True)
        
        coords_list = []
        for user_id in user_id_list:
            coord = RealTimeLocationService.get_participant_coords(user_id)
            if coord:  # None은 건너뜀
                coords_list.append(coord)

        return json.dumps(coords_list)