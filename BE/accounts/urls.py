# BE/accounts/urls.py

from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views
from .views import (
    LoginAPIView,
    RegisterAPIView,
    DeleteSoftDeletedAccountsAPIView,
    VerifyPasswordAPIView,
    UserMeAPIView,
    PasswordChangeAPIView,
    PasswordResetAPIView,
    AccountSoftDeleteAPIView,
    VerifyEmailAPIView,
    )

app_name = 'accounts'

urlpatterns = [
    # HTML 렌더링 뷰 (템플릿만 반환)
    # path('login-page/', LoginPageView.as_view(), name='login-page'),

    # API 전용 URL (axios가 호출)
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    # path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    path('block/<int:user_id>/', BlockUserView.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', UnblockUserView.as_view(), name='unblock-user'),

    path('me/', UserMeAPIView.as_view(), name='me'),
    
    # 이메일 인증 엔드포인트 연결
    path('verify-email/<uidb64>/<token>/',VerifyEmailAPIView.as_view(),name='verify-email'),
   
    # 비밀번호 재설정 검증 엔드포인트는 구현 전이므로 일단 주석
    # path('password-reset/<uidb64>/<token>/',PasswordResetAPIView.as_view(),name='password-reset'),
]