from django.urls import path
from .views import *

app_name = 'chatroom'

urlpatterns = [
    # path('schedules/', ScheduleListCreateView.as_view(), name = 'schedule-list-create'),
    # path('schedules/<int:pk>', ScheduleDetailView.as_view(), name = 'schedule-detail'),
    # path('schedules/<int:pk>/available-times/', ScheduleAvailableTimesView.as_view(), name='schedule-available-times'),
    # path('schedules/<int:pk>/select-available-time/', ScheduleSelectAvailableTimeView.as_view(), name = 'schedule-select-available-time'),
]

