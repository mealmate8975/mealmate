from django.shortcuts import render, get_object_or_404
from schedules.models import Schedules
import json

def map_view(request):
    schedule_id = request.GET.get("schedule_id")

    # 1. schedule_id 없을 경우 폼만 보여줌
    if not schedule_id:
        return render(request, 'map/map_form.html')
    
    # 2. 스케줄 조회
    schedule = get_object_or_404(Schedules, schedule_id=schedule_id)
    coord = schedule.schedule_condition or {}

    
    # 3. 좌표 추출 (예외 방지용 기본값 처리)
    try:
        coords = {
            "lat": coord["latitude"],
            "lng": coord["longitude"]
        }
    except KeyError:
        coords = {
            "lat": 37.5665,
            "lng": 126.9780
        }
    return render(request, 'map/map.html', {
    "coords": json.dumps(coords)
    })