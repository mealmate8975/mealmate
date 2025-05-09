from django.urls import path
from .views import SendFriendRequestView

urlpatterns = [
    path('send/', SendFriendRequestView.as_view(), name='friendship-send'),
]