from django.urls import path
from .views import (
    CheckParticipantView,
    ConfirmedChatRoomsView,
    UnconfirmedChatRoomsView,
    OnGoingChatRoomsView,
    UserSchedulesView,
)

app_name = "chatroom"

urlpatterns = [
    path('chatrooms/<int:chatroom_id>/check-participant/', CheckParticipantView.as_view(), name='check_participant'),
    path('chatrooms/confirmed/', ConfirmedChatRoomsView.as_view(), name='confirmed_chatrooms'),
    path('chatrooms/unconfirmed/', UnconfirmedChatRoomsView.as_view(), name='unconfirmed_chatrooms'),
    path('chatrooms/ongoing/',OnGoingChatRoomsView.as_view(), name='ongoing_chatrooms'),
    path('chatrooms/schedules/', UserSchedulesView.as_view(), name='user_schedules'),    
]