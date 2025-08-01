'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

recommendation_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''
from accounts.models import CustomUser
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

# model
from schedules.models import Schedules

class ScheduleFrequencyAnalyzer:
    def calculate_monthly_average_meetings_over_3_months():
        # 가장 최근 약속에서 만난 사람을 순차적으로 계산
        current_month = datetime.now().month
        average_list = []
        for month in range(current_month,current_month-3):
            Schedules.objects.filter(created_at__month=month)
            average = 
            average_list.append(average)
        

class ScheduleRecommendationService:
    pass