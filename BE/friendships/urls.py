from django.urls import path
from .views import *

urlpatterns = [
    path('send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('accept/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('decline/', DeclineFriendRequestView.as_view(), name='decline-friend-request'),
    path('cancle/', CancelFriendRequestView.as_view(), name='cancel-friend-request'),
    path('delete/', DeleteFriendView.as_view(), name='delete-friendship'),
]