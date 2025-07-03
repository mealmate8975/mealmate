from django.urls import path
from .views import (
    CheckParticipantView,
    ConfirmedChatRoomsView,
    UnconfirmedChatRoomsView,
    OnGoingChatRoomsView,
    UserSchedulesView,
    InviteFriendForHostView,
    InviteFriendForGuestView,
    ApproveInvitationView,
    AcceptInvitationView,
    RejectInvitationView,
    내가받은초대리스트조회View,
)

app_name = "chatroom"

urlpatterns = [
    path('chatrooms/<int:chatroom_id>/check-participant/', CheckParticipantView.as_view(), name='check_participant'),
    path('chatrooms/confirmed/', ConfirmedChatRoomsView.as_view(), name='confirmed-ongoing'),
    path('chatrooms/unconfirmed/', UnconfirmedChatRoomsView.as_view(), name='unconfirmed'),
    path('chatrooms/ongoing/',OnGoingChatRoomsView.as_view(), name='ongoing'),
    path('chatrooms/schedules/', UserSchedulesView.as_view(), name='user_schedules'),  
    path('chatrooms/invite-friend-for-host/<int:chatroom_id>/<int:target_user_id>/',InviteFriendForHostView.as_view(),name='invite_friend_for_host'),    
    path('chatrooms/invite-friend-for-guest/<int:chatroom_id>/<int:target_user_id>/',InviteFriendForGuestView.as_view(),name='invite_friend_for_guest'),    
    path('chatrooms/approve-invitation/<int:schedule_id>/<int:guest_id>/<int:target_user_id>',ApproveInvitationView.as_view(),name='approve_invitation'),
    path('chatrooms/accept-invitation/<int:invitation_id>',AcceptInvitationView.as_view(),name='accept_invitation'),
    path('chatrooms/reject-invitation/<int:invitation_id>',RejectInvitationView.as_view(),name='reject_invitation'),
    path('chatrooms/내가받은초대리스트조회',내가받은초대리스트조회View.as_view(),name='내가받은초대리스트조회'),
]