from django.urls import path
from .views import ScheduleListCreateView, ScheduleDetailView

app_name = 'schedules'

urlpatterns = [
    path('schedules/', ScheduleListCreateView.as_view(), name = 'schedule-list-create'),
    path('schedules/<int:pk>', ScheduleDetailView.as_view(), name = 'schedule-detail'),
]

