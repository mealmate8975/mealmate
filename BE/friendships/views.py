from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Friendship
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

    def post(self, request):  # POST 요청을 처리하는 메서드
        to_user_id = request.data.get('to_user_id')  # 요청 데이터에서 'to_user_id' 가져오기
        
        # 주어진 ID로 사용자를 데이터베이스에서 검색
        to_user = User.objects.get(id=to_user_id)  # ID에 해당하는 사용자 객체를 가져오기
        
        # Friendship 모델을 사용하여 친구 요청을 생성
        Friendship.objects.create(from_user=request.user, to_user=to_user, status='pending')  # 현재 로그인한 사용자(request.user)와 대상 사용자(to_user) 간의 친구 요청을 생성
        
        # 친구 요청이 성공적으로 생성되었음을 나타내는 응답 반환
        return Response({'status': '요청 보냄'}, status=201) # HTTP 상태 코드는 201(Created)

class AcceptFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

    def post(self, request): # POST 요청을 처리하는 메서드
        friendship_id = request.data.get('friendship_id') # 요청 데이터에서 'friendship_id' 가져오기

        # 친구요청 수신자가 현재 로그인한 유저이고 friendship_id가 일치하는 친구요청 객체 가져오기
        friendship = get_object_or_404(Friendship,to_user=request.user,id=friendship_id) 
        
        # 중복 수락 방지 로직
        if friendship.status == 'accepted':
            return Response({'error': '이미 수락된 요청입니다.'}, status=400)
        
        friendship.status = 'accepted' 
        friendship.save()

        # 친구 요청이 pending에서 accepted로 성공적으로 수정되었다는 응답 반환
        # HTTP 상태 코드는 200(OK) 요청이 성공적으로 처리되었음
        return Response({'status': '친구 요청 수락'}, status=200) 

