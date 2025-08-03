# BE/accounts/accounts_service.py

import re

from django.contrib.auth import get_user_model

from .models import UserBlock

User = get_user_model()

class AccountService:
    def register(validated_data):
        """
        회원가입
        """
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            phone=validated_data["phone"],
            nickname=validated_data["nickname"],
            gender=validated_data["gender"]
        )
    
    def patch_my_info(user,data):
        "회원정보 수정"
        nickname = data.get('nickname')
        phone = data.get('phone')

        if not nickname and not phone:
            return "수정할 항목이 없습니다.",400

        if nickname and User.objects.exclude(id=user.id).filter(nickname=nickname).exists():
            return "이미 사용 중인 닉네임입니다.",400
        
        if phone and not re.match(r'01[016789]\d{7,8}$',phone):
            return "전화번호 형식이 올바르지 않습니다.",400
        
        if 'nickname' in data:
            user.nickname = nickname

        if 'phone' in data:
            user.phone = phone
        
        user.save()

        return None,200
    
class BlockUserService:
    @staticmethod
    def block_user(blocker, blocked_user_id):
        """
        유저 차단을 처리합니다.
        """
        try:
            blocked_user = User.objects.get(id=blocked_user_id)

            if blocker == blocked_user:
                return {
                    "success": False,
                    "error": "자기 자신을 차단할 수 없습니다."
                }, 400
            relation_qs = UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user)
            if relation_qs.exists():
                return {
                    "success": False,
                    "error": "이미 차단된 유저입니다."
                }, 400
            
            relation_qs.create(blocker=blocker, blocked_user=blocked_user)
            return {
                "success": True,
                "message": "유저가 차단되었습니다."
            }, 200
            
        except User.DoesNotExist:
            return {
                "success": False,
                "error": "존재하지 않는 유저는 차단할 수 없습니다."
            }, 404
    
    @staticmethod
    def unblock_user(blocker, blocked_user_id):
        """
        유저 차단 해제를 처리합니다.
        """
        try:
            blocked_user = User.objects.get(id=blocked_user_id)

            if blocker == blocked_user:
                return {
                    "success": False,
                    "error": "자기 자신을 차단해제할 수 없습니다."
                }, 400

            if not UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user).exists():
                return {
                    "success": False,
                    "error": "해제할 차단이 존재하지 않습니다."
                }, 404

            UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user).delete()
            return {
                "success": True,
                "message": "유저 차단이 해제되었습니다."
            }, 200
        
        except User.DoesNotExist:
            return {
                "success": False,
                "error": "존재하지 않는 유저는 차단해제할 수 없습니다."
            }, 404