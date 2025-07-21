from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import MyTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include("accounts.urls", namespace="accounts")),
    # path('accounts/',include('accounts.urls')),
    path('friendships/',include('friendships.urls')),
    path('api/schedules/',include('schedules.urls', namespace="schedules")),
    path('api/chatroom/',include('chatroom.urls',namespace="chatroom")),
    path('chat-test/', lambda request: render(request, 'chat_test.html')),
    path('api/accounts/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 토큰 재발급
    path('api/map/', include('map.urls',namespace="map")),
    path('api/pages/', include('pages.urls',namespace="pages")),
    path('api/posts/', include('posts.urls',namespace="posts")),
]
