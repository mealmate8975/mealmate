from django.urls import path
from .views import check_participant_view

app_name = "chatroom"

urlpatterns = [
    path('chatrooms/<int:chatroom_id>/check-participant/', check_participant_view),
]
