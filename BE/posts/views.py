'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

posts_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''
from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
# from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# from .serializers import PostSerializer
from .models import Post
from pages.models import Page

from .posts_service import toggle_like as toggle_like_service, create_post

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

@login_required
def create_post_view(request, page_id=None):
    page = None
    if page_id is not None:
        page = get_object_or_404(Page, id=page_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        type_ = request.POST.get('type')
        image = request.FILES.get('image')
        create_post(request.user, page, content, type_, image)
        if page == None:
            return redirect('posts:feed_view')
        return redirect('pages:page_detail',page_id=page_id)
    
    return render(request, 'posts/post_form.html', {'page': page})
