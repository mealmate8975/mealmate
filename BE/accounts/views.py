from django.shortcuts import render
from .models import UserBlock
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()

class BlockUserService:
    @staticmethod
    def block_user(blocker, blocked_user_id):
        """
        유저 차단을 처리합니다.
        """
        try:
            blocked_user = User.objects.get(id=blocked_user_id)

            if blocker == blocked_user:
                return {"error": "자기 자신을 차단할 수 없습니다."}, 400
            
            if UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user).exists():
                return {"error": "이미 차단된 유저입니다."}, 400
            
            UserBlock.objects.create(blocker=blocker, blocked_user=blocked_user)
            return {"message": "유저가 차단되었습니다."}, 200
            
        except User.DoesNotExist:
            return {"error": "존재하지 않는 유저는 차단할 수 없습니다."}, 404
    
    @staticmethod
    def unblock_user(blocker, blocked_user_id):
        """
        유저 차단 해제를 처리합니다.
        """
        try:
            blocked_user = User.objects.get(id=blocked_user_id)

            if blocker == blocked_user:
                return {"error": "자기 자신을 차단해제할 수 없습니다."}, 400

            if not UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user).exists():
                return {"error": "해제할 차단이 존재하지 않습니다."}, 404

            UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user).delete()
            return {"message": "유저 차단이 해제되었습니다."}, 200
        except:
            return {"error": "존재하지 않는 유저는 차단해제할 수 없습니다."}, 404
# 차단
class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        return Response(*BlockUserService.block_user(request.user, user_id))
# 차단 해제
class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        return Response(*BlockUserService.unblock_user(request.user, user_id))
    
