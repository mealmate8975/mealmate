from django.urls import path
from .views import (
    feed_view,
    toggle_like,
    create_post_view,
    delete_post_view,    
)

app_name = "posts"

urlpatterns = [
    path('feed/', feed_view, name='feed_view'),                         #전체 포스트 피드
    # path('', ?.as_view(), name='?'),                                  # /<id>/     게시글 상세
    path('like/<int:post_id>/', toggle_like, name='toggle_like'),
    path('new', create_post_view, name='create_post_view'),
    path('delete/<int:post_id>/',delete_post_view, name='delete_post_view'),
]