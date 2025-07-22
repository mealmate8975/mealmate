from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# from .serializers import PostSerializer
from .models import Post

from .posts_service import toggle_like as toggle_like_service

def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/feed.html',{'posts':posts})

# class PostListAPI(generics.ListAPIView):
#     queryset = Post.objects.all().order_by('-created_at')
#     serializer_class = PostSerializer

@login_required
def toggle_like(request,post_id):
    toggle_like_service(request.user,post_id)
    return redirect(request.META.get('HTTP_REFERER','/')) # 요청을 보낸 페이지의 주소(이전 페이지 URL)를 가져오기 위해 사용되는 패턴