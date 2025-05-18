from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Friendship
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class FriendRequestService:
    @staticmethod # 정적 메서드로 선언해서 서비스 객체 없이 호출 가능
    def send_friend_request(from_user, to_user):
        forward = Friendship.objects.filter(from_user=from_user, to_user=to_user) 
        backward = Friendship.objects.filter(from_user=to_user, to_user=from_user)

        if forward.exists() or backward.exists():# 이미 존재한다면 새로운 요청을 생성하지 않고 기존 레코드의 status만 수정하기
            if forward.exists(): # 정방향 요청이 존재할 경우
                forward_target = forward.first() 
                if forward_target.status == 'pending': # 기존 친구요청이 수락 대기중일 경우
                    return {'error': '이미 보낸 친구요청'}, 400
                elif forward_target.status == 'accepted':
                    return {'error': '이미 수락된 친구요청'}, 400
                elif forward_target.status == 'declined': # 기존에 거절된 친구요청의 경우
                    forward_target.status = 'pending' # 재요청
                    forward_target.save()
                    return {'message': '친구 재요청 완료'}, 200
            else:
                backward_target = backward.first()
                if backward_target.status == 'pending': # 기존 역방향 친구요청이 수락 대기중일 경우
                    backward_target.status = 'accepted' # 양방향 친구 요청 -> 친구관계 성립으로
                    # 친구요청 버튼 비활성화, 친구요청수락 버튼 활성화
                    # 단, 친구 요청 철회 기능이 존재할 필요가 있음
                    backward_target.save()
                    return {'message': '상호 요청으로 친구가 되었습니다.'}, 200
                elif backward_target.status == 'accepted':
                    return {'error': '이미 친구관계'}, 400
                elif backward_target.status == 'declined':
                    backward_target.from_user = from_user
                    backward_target.to_user = to_user
                    backward_target.status = 'pending'
                    backward_target.save()
                    return {'message': '친구 요청 완료'}, 200
        else: # 기존 친구 요청 레코드가 없어 새로 생성
            Friendship.objects.create(from_user=from_user, to_user=to_user, status='pending') # 현재 로그인한 사용자(request.user)와 대상 사용자(to_user) 간의 친구 요청을 생성
            return {'message': '요청 보냄'}, 201 # 친구 요청이 성공적으로 생성되었음을 나타내는 응답 반환

class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

    def post(self, request):  # POST 요청을 처리하는 메서드
        to_user_id = request.data.get('to_user_id')  # 요청 데이터에서 'to_user_id' 가져오기
        
        # 주어진 ID로 사용자를 데이터베이스에서 검색
        to_user = get_object_or_404(User, id=to_user_id)  # ID에 해당하는 사용자 객체를 가져오기

        # FriendshipService 클래스의 정적 메서드를 호출하여 친구 요청 처리 로직 실행
        # request.user: 현재 로그인한 사용자 (친구 요청을 보내는 사람)
        # to_user: 요청을 받을 대상 사용자
        response_data, status_code = FriendRequestService.send_friend_request(request.user, to_user)

        # service 메서드로부터 반환된 응답 데이터와 상태 코드를 기반으로 클라이언트에 응답 반환
        return Response(response_data, status=status_code)

class FriendAcceptService:
    ERROR_RESPONSE = {'error': '수락할 수 없는 요청입니다.'}, 400

    @staticmethod
    def accept_friend_request(from_user, to_user):
        try:
            friend_request = Friendship.objects.get(from_user=from_user, to_user=to_user)
        except Friendship.DoesNotExist:
            return FriendAcceptService.ERROR_RESPONSE

        if friend_request.status != 'pending':
            return FriendAcceptService.ERROR_RESPONSE

        friend_request.status = 'accepted'
        friend_request.save()
        return {'message': '친구 요청 수락 완료'}, 200

class FriendAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from_user = request.data.get('from_user_id')
        response_data, status_code = FriendAcceptService.accept_friend_request(from_user,request.user)

        # accept_friend_request 메서드로부터 반환된 응답 데이터와 상태 코드를 기반으로 클라이언트에 응답 반환
        return Response(response_data, status=status_code)

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

# class FriendDeclineService:
#     pass

# class DeclineFriendView(APIView):
#     pass

# class FriendRequesWithdrawservice:
#     pass

# class WithDrawFriendRequestView(APIView):
#     pass