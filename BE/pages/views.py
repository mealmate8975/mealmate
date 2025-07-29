from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
# from rest_framework import generics
from rest_framework.response import Response

from .serializers import PageSerializer
from posts.serializers import PostSerializer

from .models import Page
from posts.models import Post

# def page_detail(request,page_id):
#     page = get_object_or_404(Page,id=page_id)
#     posts = Post.objects.filter(page=page)
#     ordered_posts = posts.order_by('-created_at')
#     return render(request, 'pages/detail.html',{'page':page,'posts':ordered_posts})

class PageDetailAPIView(APIView):
    def get(self,request,pk):
        page = get_object_or_404(Page,pk=pk)

        # Page 객체를 직렬화하여 딕셔너리 형태의 JSON 데이터로 변환
        page_data = PageSerializer(page).data

        # 해당 페이지에 연결된 포스트(Post)를 최신순으로 정렬
        posts = page.posts.order_by('-created_at')

        # 정렬된 포스트 목록을 직렬화하여 JSON 형태로 변환하고, page_data에 'posts' 키로 추가
        page_data['posts'] = PostSerializer(posts,many=True).data
        
        # 전체 page + posts 데이터를 JSON 응답으로 반환
        return Response(page_data)