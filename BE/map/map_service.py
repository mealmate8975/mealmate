'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

map_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''

class MapSerive:
    def update_coords():
        pass

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