from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Friendship
from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404

User = get_user_model()

class FriendRequestService:
    @staticmethod
    def _handle_forward_existing(forward_first):
        """
        이미 존재하는 정방향 친구 요청 처리:
        - pending: 중복 요청 오류 반환
        - accepted: 이미 친구임
        - declined: 재요청 처리
        """
        if forward_first.status == 'pending':
            return {'error': '이미 보낸 친구요청'}, 400
        elif forward_first.status == 'accepted':
            return {'error': '이미 수락된 친구요청'}, 400
        elif forward_first.status == 'declined':
            forward_first.status = 'pending'
            forward_first.save()
            return {'message': '친구 재요청 완료'}, 200
        else:
            return {'error': '유효하지 않은 요청'}, 400 
        
    @staticmethod
    def _handle_backward_existing(backward_first):
        if backward_first.status == 'pending': # 기존 역방향 친구요청이 수락 대기중일 경우
            backward_first.status = 'accepted' # 양방향 친구 요청 -> 친구관계 성립으로
            # 친구요청 버튼 비활성화, 친구요청수락 버튼 활성화
            # 단, 친구 요청 철회 기능이 존재할 필요가 있음
            backward_first.save()
            return {'message': '상호 요청으로 친구가 되었습니다.'}, 200
        elif backward_first.status == 'accepted':
            return {'error': '이미 친구관계'}, 400
        elif backward_first.status == 'declined':
            backward_first.status = 'pending'
            tmp = backward_first.from_user
            backward_first.from_user = backward_first.to_user
            backward_first.to_user = tmp
            backward_first.save()
            return {'message': '친구 요청 완료'}, 200
        else:
            return {'error': '유효하지 않은 요청'}, 400 

    @staticmethod # 정적 메서드로 선언해서 서비스 객체 없이 호출 가능
    def send_friend_request(from_user, to_user):
        forward = Friendship.objects.filter(from_user=from_user, to_user=to_user) 
        backward = Friendship.objects.filter(from_user=to_user, to_user=from_user)

        if forward.exists():
            return FriendRequestService._handle_forward_existing(forward.first())
        elif backward.exists():
            return FriendRequestService._handle_backward_existing(backward.first())
        else: # 기존 친구 요청 레코드가 없어 새로 생성
            Friendship.objects.create(from_user=from_user, to_user=to_user, status='pending') # 현재 로그인한 사용자(request.user)와 대상 사용자(to_user) 간의 친구 요청을 생성
            return {'message': '요청 보냄'}, 201 # 친구 요청이 성공적으로 생성되었음을 나타내는 응답 반환
        
class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 이 뷰에 접근하기 위해 사용자가 인증되어야 함을 설정

    def post(self, request):  # POST 요청을 처리하는 메서드
        to_user_id = request.data.get('to_user_id')  # 요청 데이터에서 'to_user_id' 가져오기
        
        # 주어진 ID로 사용자를 데이터베이스에서 검색
        try:
            to_user = User.objects.get(id=to_user_id)  # ID에 해당하는 사용자 객체를 가져오기
        except User.DoesNotExist:
            return Response({'error': '요청을 처리할 수 없습니다.'}, status=404)
        # FriendshipService 클래스의 정적 메서드를 호출하여 친구 요청 처리 로직 실행
        # request.user: 현재 로그인한 사용자 (친구 요청을 보내는 사람)
        # to_user: 요청을 받을 대상 사용자
        response_data, status_code = FriendRequestService.send_friend_request(request.user, to_user)

        # service 메서드로부터 반환된 응답 데이터와 상태 코드를 기반으로 클라이언트에 응답 반환
        return Response(response_data, status=status_code)

# friendship 삭제 로직 (1.친구요청 철회와 2.친구 삭제의 공통 로직)
class FriendshipDeletionService:
    @staticmethod
    def delete_friendship_if_exists(queryset):
        if queryset.exists():
            queryset.delete()
            return {"message": "친구 관계가 삭제되었습니다."}, 200
        return {"error": "삭제할 수 있는 친구 관계가 존재하지 않습니다."}, 404

# 친구요청 철회 기능 (공통 삭제 로직을 이용하도록 수정)
class FriendRequestCancelService:
    @staticmethod
    def cancel_request(from_user, to_user):
        queryset = Friendship.objects.filter(
            from_user=from_user, 
            to_user=to_user, 
            status='pending'
        )
        return FriendshipDeletionService.delete_friendship_if_exists(queryset)

# 친구요청 철회 기능(수정 전)
class FriendRequestCancelService:
    @staticmethod
    def cancel_request(from_user, to_user):
        try:
            # 보낸 요청중 아직 대기중인 것
            requested_friendship = Friendship.objects.filter(from_user=from_user, to_user = to_user, status = 'pending')
        except Friendship.DoesNotExist:
            return {"error" : "친구요청이 존재하지 않습니다."}, 404
        requested_friendship.delete()
        return {"message" : "친구요청이 취소되었습니다."}, 200

class CancelFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request):
        to_user_id = request.data.get('to_user_id')
        try:
            to_user = User.objects.get(id=to_user_id)  # ID에 해당하는 사용자 객체를 가져오기
        except User.DoesNotExist:
            return Response({'error': '요청을 처리할 수 없습니다.'}, status=404)  # 404 상태 코드 반환

        response_data, status_code = FriendRequestCancelService.cancel_request(
            from_user = request.user, 
            to_user = to_user 
        )
        return Response(response_data, status=status_code)

# 거절과 수락의 공통 로직
class FriendRequestStatusUpdateService:
    @staticmethod
    def handle_request(from_user, to_user, new_status, success_message):
        try:
            friend_request = Friendship.objects.get(from_user=from_user, to_user=to_user)
        except Friendship.DoesNotExist:
            return {'error': '요청을 처리할 수 없습니다.'}, 404

        if friend_request.status != 'pending':
            return {'error': '이미 처리된 친구 요청입니다.'}, 400

        friend_request.status = new_status
        friend_request.save()
        return {'message': success_message}, 200
class AcceptFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from_user_id = request.data.get('from_user_id')
        try:
            from_user = User.objects.get(id = from_user_id)
        except User.DoesNotExist:
            return Response({'error': '요청을 처리할 수 없습니다.'}, status=404)
        
        response_data, status_code = FriendRequestStatusUpdateService.handle_request(
            from_user=from_user,
            to_user=request.user,
            new_status='accepted',
            success_message='친구 요청 수락 완료'
        )
        return Response(response_data, status=status_code)
class DeclineFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from_user_id = request.data.get('from_user_id')
        try:
            from_user = User.objects.get(id = from_user_id)
        except User.DoesNotExist:
            return Response({'error': '요청을 처리할 수 없습니다.'}, status=404)

        response_data, status_code = FriendRequestStatusUpdateService.handle_request(
            from_user=from_user,
            to_user=request.user,
            new_status='declined',
            success_message='친구 요청 거절 완료'
        )
        return Response(response_data, status=status_code)
    
# 친구 삭제 기능(수정 전)
# class FriendDeleteService:
#     @staticmethod
#     def delete_friend(from_user, to_user):
#         forward = Friendship.objects.filter(from_user=from_user, to_user=to_user,status='accepted')
#         backward = Friendship.objects.filter(from_user=to_user, to_user=from_user,status='accepted')

#         forward_exists = forward.exists()
#         backward_exists = backward.exists()

#         if forward_exists or backward_exists:
#             if forward_exists:
#                 target = forward.first()
#             elif backward_exists:
#                 target = backward.first()
#             target.delete()
#             return {"message" : "친구 관계가 삭제되었습니다."}, 200
#         else:
#             return {"error" : "삭제할 수 있는 친구 관계가 존재하지 않습니다."}, 404

# 친구 삭제 기능 (공통 삭제 로직을 이용하도록 수정)
class FriendDeleteService:
    @staticmethod
    def delete_friend(from_user, to_user):
        queryset = Friendship.objects.filter(from_user=from_user, to_user=to_user, status='accepted') | Friendship.objects.filter(
        from_user=to_user, to_user=from_user, status='accepted')
        return FriendshipDeletionService.delete_friendship_if_exists(queryset)

class DeleteFriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': '요청을 처리할 수 없습니다.'}, status=404)

        response_data, status_code = FriendDeleteService.delete_friend(request.user, to_user)
        return Response(response_data, status=status_code)

# 친구 차단 기능
# class FriendBanService:
#     pass
# class BanFriendView(APIView):
#     pass