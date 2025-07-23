from django.urls import path
from .views import (
    feed_view,
    toggle_like,    
)

app_name = "posts"

urlpatterns = [
    path('feed/', feed_view, name='feed_view'),      #전체 포스트 피드
    # path('', ?.as_view(), name='?'),      # /<id>/     게시글 상세
    path('like/<int:post_id>/', toggle_like, name='toggle_like'),
    path('like/<int:post_id>/', toggle_like, name='toggle_like'),
]