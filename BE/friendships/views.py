from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Friendship
from django.contrib.auth import get_user_model

User = get_user_model()

class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

    def post(self, request):  # POST 요청을 처리하는 메서드
        to_user_id = request.data.get('to_user_id')  # 요청 데이터에서 'to_user_id'를 가져오기
        
        # 주어진 ID로 사용자를 데이터베이스에서 검색
        to_user = User.objects.get(id=to_user_id)  # ID에 해당하는 사용자 객체를 가져오기
        
        # Friendship 모델을 사용하여 친구 요청을 생성
        Friendship.objects.create(from_user=request.user, to_user=to_user, status='pending')  # 현재 로그인한 사용자(request.user)와 대상 사용자(to_user) 간의 친구 요청을 생성
        
        # 친구 요청이 성공적으로 생성되었음을 나타내는 응답을 반환
        return Response({'status': '요청 보냄'}, status=201) # HTTP 상태 코드는 201(Created)