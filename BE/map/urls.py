from django.urls import path
from .views import (
    UpdateRealTimeLocationView
)

app_name = "map"

urlpatterns = [
    # path('', views.map_view, name='map_view'),
    path('location/<int:schedule_id>/', UpdateRealTimeLocationView.as_view(), name='update_real_time_location'),
]