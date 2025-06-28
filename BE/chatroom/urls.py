from django.urls import path
from .views import (
    CheckParticipantView,
    ConfirmedChatRoomsView,
    UnconfirmedChatRoomsView,
    OnGoingChatRoomsView,
    UserSchedulesView,
    InviteFriendForHostView,
)

app_name = "chatroom"

urlpatterns = [
    path('chatrooms/<int:chatroom_id>/check-participant/', CheckParticipantView.as_view(), name='check_participant'),
    path('chatrooms/confirmed/', ConfirmedChatRoomsView.as_view(), name='confirmed-ongoing'),
    path('chatrooms/unconfirmed/', UnconfirmedChatRoomsView.as_view(), name='unconfirmed'),
    path('chatrooms/ongoing/',OnGoingChatRoomsView.as_view(), name='ongoing'),
    path('chatrooms/schedules/', UserSchedulesView.as_view(), name='user_schedules'),  
    path('chatrooms/invite-friend-for-host/<int:chatroom_id>/<int:target_user_id>/',InviteFriendForHostView.as_view(),name='invite_friend_for_host'),    
]