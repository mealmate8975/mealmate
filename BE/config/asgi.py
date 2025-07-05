import os
from django.core.asgi import get_asgi_application

# 환경변수 먼저 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 1️⃣ Django 애플리케이션 먼저 초기화 (이 시점 이후 Django ORM 접근 가능)
django_asgi_app = get_asgi_application()

# 2️⃣ Django 초기화 이후에 channels import (여기서부터 import 해야 안전함)
from channels.routing import ProtocolTypeRouter, URLRouter
from chatroom.middleware import JWTAuthMiddlewareStack  # 이제 여기서 import 가능
import chatroom.routing

# 3️⃣ 전체 ASGI 애플리케이션 정의
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # HTTP 요청은 기존 Django가 처리
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            chatroom.routing.websocket_urlpatterns
        )
    ),
})