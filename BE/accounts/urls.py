# BE/accounts/urls.py

from django.urls import path
from . import views
from .views import *

app_name = 'accounts'

urlpatterns = [
    #회원가입
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/',VerifyEmailAPIView.as_view(),name='verify-email'), # 이메일 인증 엔드포인트 연결

    #로그인
    path('login/', LoginAPIView.as_view(), name='login'),

    #내정보
    path('me/', UserMeAPIView.as_view(), name='me'), # 내 회원 정보 조회
    
    #비밀번호
    path('password-change/',PasswordChangeAPIView.as_view(),name='password-change'), # 비밀번호 변경
    path('password-reset/',PasswordResetRequestAPIView.as_view(),name='password-reset-request'), # 비밀번호 재설정 요청
    path('password-reset/<uidb64>/<token>/',PasswordResetConfirmAPIView.as_view(),name='password-reset-confirm'), # 비밀번호 재설정 검증 엔드포인트

    #차단
    path('block/<int:user_id>/', BlockUserView.as_view(), name='block-user'), # 유저 차단
    path('unblock/<int:user_id>/', UnblockUserView.as_view(), name='unblock-user'), # 유저 차단 해제
    path('blocked-users/',GetBlockedUserView.as_view(),name='blocked-users'),# 차단 유저 목록 보기

    #탈퇴
    path('soft-delete/',AccountSoftDeleteAPIView.as_view(),name='account-soft-delete'), # 계정 탈퇴(soft delete)
    path('delete-soft-deleted-accounts/',DeleteSoftDeletedAccountsAPIView.as_view(),name='delete-soft-deleted-accounts'), # 계정 삭제
]