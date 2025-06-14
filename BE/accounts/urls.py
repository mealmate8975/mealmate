from django.urls import path
from . import views
from .views import *

app_name = 'accounts'

urlpatterns = [
    # HTML 렌더링 뷰 (템플릿만 반환)
    path('login-page/', LoginPageView.as_view(), name='login-page'),

    # API 전용 URL (axios가 호출)
    path('login/', LoginAPIView.as_view(), name='login'),
    
    path('register/', views.RegisterView.as_view(), name='register'),
    path('block/<int:user_id>/', BlockUserView.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', UnblockUserView.as_view(), name='unblock-user'),
]