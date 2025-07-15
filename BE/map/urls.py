from django.urls import path
from .views import (
    UpdateRealTimeLocationView,
    SendUpdatedCoordinatesView
)

app_name = "map"

urlpatterns = [
    # path('', views.map_view, name='map_view'),
    path('location/<int:schedule_id>/', UpdateRealTimeLocationView.as_view(), name='update_real_time_location'),
    path('location/stream/', SendUpdatedCoordinatesView.as_view(), name='stream_location'),
]