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
        to_user = get_object_or_404(User, id=to_user_id)  # ID에 해당하는 사용자 객체를 가져오기

        # 친구 요청 생성 전
        # 기존 친구 요청이 존재하는지 확인하고 (역방향도 해당) 
        forward = Friendship.objects.filter(from_user = request.user,to_user= to_user) # 요청과 같은 방향
        backward = Friendship.objects.filter(from_user = to_user,to_user= request.user) # 역방향
        
        if forward.exists() or backward.exists(): # 있다면 새로운 요청을 생성하지 않고 기존 레코드의 status만 수정하기
            if forward.exists(): # 정방향 요청이 존재할 경우
                forward_target = forward.first()
                if forward_target.status == 'pending': # 기존 친구요청이 'pending'일 경우
                    return Response({'error': '이미 보낸 친구요청'},status=400) # 400(Bad Request)
                elif forward_target.status == 'accepted':
                    return Response({'error': '이미 수락된 친구요청'},status=400) # 400(Bad Request)
                elif forward_target.status == 'declined': # 기존 거절된 친구요청의 경우
                    forward_target.status = 'pending' # 재요청
                    forward_target.save()
                    return Response({'message': '친구 재요청 완료'}, status=200)  
            else: # 역방향 요청이 존재할 경우
                backward_target = backward.first()
                if backward_target.status == 'pending': # 기존 역방향 친구요청이 'pending'일 경우
                    backward_target.status = 'accepted' # 양방향 친구 요청 -> 친구관계 성립으로
                    # 단, 친구 요청 철회 기능이 존재할 필요가 있음
                    backward_target.save()
                elif backward_target.status == 'accepted':
                    return Response({'error': '이미 친구관계'},status=400) # 400(Bad Request)
                elif backward_target.status == 'declined': # 기존에 내가 거절한 역방향의 친구요청의 경우
                    # from_user와 to_user의 값을 바꾸고 status를 pending으로 전환
                    backward_target.from_user = request.user
                    backward_target.to_user = to_user
                    backward_target.save()
                    return Response({'message': '친구 요청 완료'}, status=200)  
        else: # 기존 친구 요청 레코드가 없어 새로 생성
            # 친구 요청 생성
            Friendship.objects.create(from_user=request.user, to_user=to_user, status='pending')  # 현재 로그인한 사용자(request.user)와 대상 사용자(to_user) 간의 친구 요청을 생성
            # 친구 요청이 성공적으로 생성되었음을 나타내는 응답 반환
            return Response({'message': '요청 보냄'}, status=201) # 201(Created)

# class AcceptFriendRequestView(APIView):
#     permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

#     def post(self, request): # POST 요청을 처리하는 메서드
#         friendship_id = request.data.get('friendship_id') # 요청 데이터에서 'friendship_id' 가져오기
#         if not friendship_id: # friendship_id가 누락된 경우
#             return Response({'error': 'friendship_id는 필수입니다.'}, status=400)
        
#         # 친구요청 수신자가 현재 로그인한 유저이고 friendship_id가 일치하는 친구요청 객체 가져오기
#         friendship = get_object_or_404(Friendship,to_user=request.user,id=friendship_id) 
        
#         # 중복 수락 방지 로직
#         if friendship.status == 'accepted':
#             return Response({'error': '이미 수락된 요청입니다.'}, status=400)
        
#         friendship.status = 'accepted' 
#         friendship.save()

#         # status가 accepted로 성공적으로 수정되었다는 응답 반환
#         return Response({'message': '친구요청 수락 완료'}, status=200)  # HTTP 상태 코드는 200(OK) 요청이 성공적으로 처리되었음

# class DeclineFriendRequestView(APIView):
#     permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

#     def post(self, request): # POST 요청을 처리하는 메서드
#         friendship_id = request.data.get('friendship_id') # 요청 데이터에서 'friendship_id' 가져오기
#         if not friendship_id:
#             return Response({'error': 'friendship_id는 필수입니다.'}, status=400)
        
#         # 친구요청 수신자가 현재 로그인한 유저이고 friendship_id가 일치하는 친구요청 객체 가져오기
#         friendship = get_object_or_404(Friendship,to_user=request.user,id=friendship_id) 
        
#         # 중복 거절 방지 로직
#         if friendship.status == 'declined':
#             return Response({'error': '이미 거절된 친구요청입니다.'}, status=400)
        
#         # 이미 친구요청을 수락한 경우 거절 불가
#         if friendship.status == 'accepted':
#             return Response({'error': '이미 수락한 친구요청입니다.'}, status=400)
#         # 거절이 불가능한 대신에 친구 삭제 및 차단 기능이 필요해보임
        
#         friendship.status = 'declined' 
#         friendship.save()

#         # 친구 요청이 pending에서 declined로 성공적으로 수정되었다는 응답 반환
#         return Response({'message': '친구요청 거절 완료'}, status=200) # HTTP 상태 코드는 200(OK)로 요청이 성공적으로 처리되었음
