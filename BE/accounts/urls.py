from django.urls import path
from . import views
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('block/<int:user_id>/', BlockUserView.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', UnblockUserView.as_view(), name='unblock-user'),
]