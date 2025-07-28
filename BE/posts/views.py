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
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.exceptions import PermissionDenied

from .serializers import PostSerializer
from .models import Post
from pages.models import Page

from .posts_service import toggle_like as toggle_like_service

class PostCreateAPIView(CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        page_id = self.kwargs.get('page_id')  # URL에서 page_id 추출
        page = None
        if page_id:
            page = get_object_or_404(Page,id=page_id)
        serializer.save(author=self.request.user,page=page)

class PostListAPIView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class PostUpdateAPIView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        post = self.get_object()

        if post.author != self.request.user:
            raise PermissionDenied("본인이 작성한 글만 수정할 수 있습니다.")
        
        delete_image = self.request.data.get('delete_image')
        if delete_image and post.image:
            post.image.delete(save=False)
            post.image = None
        
        serializer.save()

class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("본인이 작성한 글만 삭제할 수 있습니다.")
        instance.delete()

class ToggleLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        toggle_like_service(request.user,post_id)
        return Response({"liked":"liked"}, status=status.HTTP_200_OK)
    
# @require_GET
# def feed_view(request):
#     posts = Post.objects.all().order_by('-created_at')
#     return render(request, 'posts/feed.html',{'posts':posts})

# class PostListAPI(generics.ListAPIView):
#     queryset = Post.objects.all().order_by('-created_at')
#     serializer_class = PostSerializer

# @require_http_methods(["GET", "POST"])
# @login_required
# def create_post_view(request, page_id=None):
#     page = None
#     if page_id is not None:
#         page = get_object_or_404(Page, id=page_id)

#     if request.method == 'POST':
#         content = request.POST.get('content')
#         type_ = request.POST.get('type')
#         image = request.FILES.get('image')

#         serializer = PostSerializer(data={
#             'content': content,
#             'type': type_,
#             'page': page.id if page else None
#         })
#         serializer.is_valid(raise_exception=True)

#         create_post(request.user, page, content, type_, image)
#         if page == None:
#             return redirect('posts:feed_view')
#         return redirect('pages:page_detail',page_id=page_id)
    
#     return render(request, 'posts/post_form.html', {'page': page})


# @require_POST # 수정 버튼 구현 후 다시 활성화 할 것
# @login_required
# def update_post_view(request,post_id):
#     post = get_object_or_404(Post,id=post_id)

#     # 수정 버튼을 본인의 포스트에서만 보이도록 프론트에서 구현할 것
#     if post.author != request.user:
#         return HttpResponseForbidden("본인이 작성한 글만 수정할 수 있습니다.")
    
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         type_ = request.POST.get('type')
#         image = request.FILES.get('image')
#         delete_image = request.POST.get('delete_image')  

#         serializer = PostSerializer(data={
#             'content': content,
#             'type': type_,
#         })
#         serializer.is_valid(raise_exception=True) 

#         update_post(post,content,type_,image,delete_image)

#         page_id = post.page_id
#         if page_id is None:
#             return redirect('posts:feed_view')
#         return redirect('pages:page_detail',page_id=page_id)
    
#     return render(request, 'posts/post_form.html',{'post':post} )

# @require_POST # 삭제 버튼 구현 후 다시 활성화 할 것
# @login_required
# def delete_post_view(request,post_id,page_id=None):
#     post = get_object_or_404(Post,id=post_id)

#     # 삭제 버튼을 본인의 포스트에서만 보이도록 프론트에서 구현할 것
#     if post.author != request.user:
#         return HttpResponseForbidden("본인이 작성한 글만 삭제할 수 있습니다.")
    
#     delete_post(post)
#     if page_id is None:
#         return redirect('posts:feed_view')
#     return redirect('pages:page_detail',page_id=page_id)

# @require_POST
# @login_required
# def toggle_like(request,post_id):
#     toggle_like_service(request.user,post_id)
#     return redirect(request.META.get('HTTP_REFERER','/')) # 요청을 보낸 페이지의 주소(이전 페이지 URL)를 가져오기 위해 사용되는 패턴
