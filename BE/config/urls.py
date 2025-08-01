# from accounts.views import MyTokenObtainPairView
# from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('accounts/',include('accounts.urls')),
    # path('accounts/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('accounts/', include("accounts.urls", namespace="accounts")),
    path('friendships/',include('friendships.urls')),
    path('schedules/',include('schedules.urls', namespace="schedules")),
    path('chatroom/',include('chatroom.urls',namespace="chatroom")),
    path('chat-test/', lambda request: render(request, 'chat_test.html')),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 토큰 재발급
    path('map/', include('map.urls',namespace="map")),
    path('pages/', include('pages.urls',namespace="pages")),
    path('posts/', include('posts.urls',namespace="posts")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)