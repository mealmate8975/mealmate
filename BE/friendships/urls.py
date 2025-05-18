from django.urls import path
from .views import SendFriendRequestView,FriendAcceptView #,AcceptFriendRequestView

urlpatterns = [
    path('send/', SendFriendRequestView.as_view(), name='friendship-send'),
    path('accept/', FriendAcceptView.as_view(), name='friend-accept'),
]