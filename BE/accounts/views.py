# BE/accounts/views.py

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser

from .serializers import LoginSerializer, RegisterSerializer
from .accounts_service import AccountService, BlockUserService

User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = AccountService.register(validated_data)
            return Response({"message": "회원가입 성공",},status=201)
        error_message = next(iter(serializer.errors.values()))[0]
        return Response({
            "error": {
                "code": "invalid_registration",
                "message": error_message
            }
        }, status=400)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if not user.is_active:
                success,reason = AccountService.activate_account(user)
                if not success:
                    return Response({
                        "error": {
                            "code": "activation_failed",
                            "message": "계정 활성화에 실패했습니다."
                        }
                    }, status=500)
            

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "reason": reason,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "name": user.name,
                    "gender": user.gender,
                    "phone": user.phone
                }
            }, status=200)
        
        error_message = serializer.errors.get('non_field_errors', ["로그인 실패"])[0]
        return Response({
            "error": {
                "code": "invalid_credentials",
                "message": error_message
            }
            }, status=400)
    
class DeleteSoftDeletedAccountsAPIView(APIView):
    """
    삭제 유예기간이 끝난 유저 삭제
    """
    permission_classes = [IsAdminUser]
    def get(self,request):
        result = AccountService.delete_soft_deleted_accounts()
        if result["status"] == "error":
            return Response({
                "error": {
                    "code": "deletion_failed",
                    "message": "유저 삭제 중 서버 오류가 발생했습니다."
                }
            }, status=500)

        if result["deleted_count"] == 0:
            return Response({
                "error": {
                    "code": "no_deletion_needed",
                    "message": "삭제할 유저가 없습니다."
                }
            }, status=200)

        return Response({
            "message": {
                "code": "deletion_success",
                "message": f"{result['deleted_count']}명의 유저 삭제 완료"
            }
        }, status=200)

class UserMeView(APIView):
    """
    개인정보 확인과 수정
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "name": user.name,
                "gender": user.gender,
                "phone": user.phone
            }
        })
    
    def patch(self,request):
        data = request.data
        user = request.user
        error_msg,status_code = AccountService.patch_my_info(user,data)
        if error_msg is None:
            return Response({
            "user" :{
                "id" : user.id,
                "email": user.email,
                "nickname": user.nickname,
                "name": user.name,
                "gender": user.gender,
                "phone": user.phone
            }
        }, status=200)
        return Response({
            "error": {
                "code": "update_failed",  # 필요시 세분화 가능
                "message": error_msg
            }
        }, status=status_code)

class BlockUserView(APIView):
    """
    유저 차단
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        data, status_code = BlockUserService.block_user(request.user, user_id)

        if status_code >= 400:
            return Response(data, status=status_code)

        return Response({
            "message": {
                "code": "block_success",
                "message": data["message"]
            }
        }, status=status_code)

class UnblockUserView(APIView):
    """
    유저 차단 해제
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        data, status_code = BlockUserService.unblock_user(request.user, user_id)
        
        if status_code >= 400:
            return Response({
                "error": {
                    "code": "unblock_failed",
                    "message": data.get("error", "차단 해제 중 오류가 발생했습니다.")
                }
            }, status=status_code)

        return Response({
            "message": {
                "code": "unblock_success",
                "message": data["message"]
            }
        }, status=status_code)

class GetBlockedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data, status_code = BlockUserService.get_blocked_user(request.user)

        if status_code >= 400:
            return Response(data, status=status_code)

        return Response(data, status=200)

# from .serializers import MyTokenObtainPairSerializer

# class RegisterView(APIView):
#     def get(self, request):
#         # 회원가입 페이지를 렌더링
#         return render(request, 'register.html')
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = User.objects.create_user(
#                 email = serializer.validated_data['email'],
#                 name = serializer.validated_data['name'],
#                 password = serializer.validated_data['password'],
#                 phone = serializer.validated_data['phone'],
#                 nickname = serializer.validated_data['nickname']
#             )
#             return Response({
#                 "message": "회원가입 성공", 'USER_ID': user.email
#             }, status=201)
#         return Response(serializer.errors, status=400)

# class LoginPageView(View):
#     def get(self, request):
#         return render(request, 'login.html')

# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer