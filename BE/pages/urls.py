from django.urls import path
from .views import (
#     pagelist_view,
    page_detail,
)
# from posts.views import create_post_view

app_name = "pages"

urlpatterns = [
    # path('pagelist/', pagelist_view, name='pagelist_view'),                     # 페이지 리스트
    path('<int:page_id>/', page_detail, name='page_detail'),                # 페이지 상세 정보 + 게시판
    # path('<int:page_id>/post/new',create_post_view , name='create_post_view'),   # 페이지에 게시글 작성
]