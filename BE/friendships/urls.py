from django.urls import path
from .views import SendFriendRequestView,AcceptFriendRequestView,DeclineFriendRequestView, CancelFriendRequestView

urlpatterns = [
    path('send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('accept/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('decline/', DeclineFriendRequestView.as_view(), name='decline-friend-request'),
    path('decline/', CancelFriendRequestView.as_view(), name='cancel-friend-request'),
]