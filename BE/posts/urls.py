from django.urls import path
from .views import (
    # feed_view,
    # toggle_like,
    # create_post_view,
    # update_post_view,
    # delete_post_view,
    PostCreateAPIView,
    PostListAPIView,
    PostUpdateAPIView,
    PostDeleteAPIView,
    ToggleLikeAPIView,
)

app_name = "posts"

urlpatterns = [    
    path('create', PostCreateAPIView.as_view(), name='create_post'),
    path('list/', PostListAPIView.as_view(), name='post_list'),                       #전체 포스트 피드
    path('update/<int:pk>/',PostUpdateAPIView.as_view(), name='post_update'),
    path('delete/<int:pk>/',PostDeleteAPIView.as_view(), name='post_delete'),
    path('like/<int:post_id>/', ToggleLikeAPIView.as_view(), name='toggle_like'),
]