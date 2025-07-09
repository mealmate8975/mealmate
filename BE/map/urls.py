from django.urls import path
from .views import (
    UpdateRealTimeLocationView
)

app_name = "map"

urlpatterns = [
    # path('', views.map_view, name='map_view'),
    path('update-real-time-location', UpdateRealTimeLocationView.as_view(), name='update_real_time_location'),
]