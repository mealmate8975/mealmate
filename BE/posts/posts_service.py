'''
SOLID 원칙을 적용한 Django REST Framework에서의 대표적인 코드 구성 방식

posts_service.py
실제 비즈니스 로직을 수행하는 서비스 계층

views.py
클라이언트의 HTTP 요청을 받고, 인증과 응답 처리만 담당하는 컨트롤러 역할의 뷰 레이어
'''
from accounts.models import CustomUser
from django.shortcuts import get_object_or_404

from .models import Post,Like

def toggle_like(user:CustomUser,post_id:int) ->bool:
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=user,post=post) 
    # like : 조회되었거나 새로 생성된 Like 객체
    # created : 객체가 새로 생성되었으면 True, 기존에 이미 있었다면 False

    if not created:
        like.delete()
        return False

    return True