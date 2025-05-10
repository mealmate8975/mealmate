from django.urls import path
from .views import SendFriendRequestView,AcceptFriendRequestView

urlpatterns = [
    path('send/', SendFriendRequestView.as_view(), name='friendship-send'),
    path('accept/', AcceptFriendRequestView.as_view(), name='friendship-accept'),
]