# BE/accounts/views.py

from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from django.db import transaction
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.conf import settings
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status

from .serializers import (
    LoginSerializer, 
    RegisterSerializer, 
    PasswordChangeSerializer,
    PasswordVerifySerializer,
    PasswordResetRequestSerializer,
)
from .accounts_service import AccountService, BlockUserService

User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = AccountService.register(validated_data)
            # 트랜잭션 커밋 후 이메일 발송
            transaction.on_commit(
                lambda: AccountService.send_verification_email(user, request)
            )
            return Response({"message": "회원가입 성공",},status=201)
        error_message = next(iter(serializer.errors.values()))[0]
        return Response({
            "error": {
                "code": "invalid_registration",
                "message": error_message
            }
        }, status=400)

class VerifyEmailAPIView(APIView):
    """
    이메일 인증: 메일 링크 클릭 시 토큰/UID 검증 후 email_verified를 갱신.
    - settings.VERIFY_EMAIL_REDIRECT 가 설정되어 있으면, 해당 URL로 결과를 쿼리스트링으로 리다이렉트
    - 없으면 JSON 응답
    """
    permission_classes = [AllowAny]

    def get(self,request,uidb64,token):
        # 1) uid → user 조회
        try:
            # uidb64 복호화 → 사용자 조회
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            return self._respond(request,400,"invalid_uid","잘못된 사용자 식별입니다.")
        except User.DoesNotExist:
            return self._respond(request,404,"user_not_found","해당 사용자를 찾을 수 없습니다.")
        
        # 2) 이미 인증된 계정
        if getattr(user,"email_verified",False):
            return self._respond(request,200,"already_verified","이미 이메일 인증이 완료되었습니다.")
        
        # 3) 토큰 검증
        if not default_token_generator.check_token(user,token): # default_token_generator.check_token(user, token) 검증
            return self._respond(request,400,"invalid_or_expired_token","토큰이 유효하지 않거나 만료되었습니다.")
        
        # 4) 인증 처리
        user.email_verified = True # 성공 시 email_verified=True 저장
        user.save(update_fields=["email_verified"])
        return self._respond(request,200,"verify_success","이메일 인증이 완료되었습니다.")
    
    def _respond(self, request, code, message, status_code):
        redirect_base = getattr(settings,"VERIFY_EMAIL_REDIRECT",None)
        if redirect_base:
            q = urlencode({"code":code,"message":message})
            sep = '&' if '?' in redirect_base else '?'
            return redirect(f"{redirect_base}{sep}{q}")
        # 리다이렉트 설정이 없으면 JSON 응답
        body = (
            {"message":{"code":code,"message":message}}
            if status_code < 400
            else {"error":{"code":code,"message":message}}
        )
        return Response(body,status=status_code)

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
    삭제 유예 기간이 끝난 유저 삭제
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

class VerifyPasswordAPIView(APIView):
    def post(self,request):
        serializer = PasswordVerifySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response({
            "message": {
                "code": "password_verified",
                "message": "비밀번호가 일치합니다."
            }
            }, status=200) # 클라이언트는 이 응답을 받으면 “비밀번호 인증 통과” 상태라고 간주하고, 다음 요청에 X-Password-Verified: true 헤더를 추가
        error = serializer.errors.get('password', [None])[0]
        error_message = str(error)
        error_code = getattr(error, 'code', 'invalid_request')

        if error_code == "incorrect_password":
            status_code = 403
        elif error_code == "required":
            status_code = 400
        else:
            status_code = 400

        return Response({
            "error": {
                "code": error_code,
                "message": error_message
            }
        }, status=status_code)

class UserMeAPIView(APIView):
    """
    개인정보 확인과 수정
    """
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
        # 비밀번호 확인이 앞서 이루어졌는지 확인(프로토타입용 임시)
        if request.headers.get("X-Password-Verified") != "true":
            return Response({
                "error":{
                    "code" : "password_verification_required",
                    "message" : "비밀번호 확인이 필요합니다."
                }
            },status=403)
        
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
                "code": "update_failed",
                "message": error_msg
            }
        }, status=status_code)
    
class PasswordChangeAPIView(APIView):
    """
    비빌번호 변경
    """
    def patch(self, request):
        serializer = PasswordChangeSerializer(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'})

class PasswordResetRequestAPIView(APIView):
    """
    이메일 입력 받고 reset 메일 보내기
    """
    permission_classes = [AllowAny]

    def post(self,request):
        serializer =  PasswordResetRequestSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        validated_email = serializer.validated_data["email"]
        data = AccountService.reset_password(validated_email,request)
        if data["code"] == "NOT_FOUND_NOOP" or data["code"] == "FOUND_SENT":
            return Response({"message": {
                "code": "password_reset_email_sent",
                "message": "비밀번호 재설정 안내를 이메일로 전송했습니다."
            }},status=200)
        return Response({
        "error": {
            "code": "password_reset_send_failed",
            "message": "이메일 전송 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
        }
        },status=500)

class PasswordResetConfirmAPIView(APIView):
    """
    토큰 검증 후 비밀번호 입력 페이지
    사용자가 이메일로 받은 uidb64와 token을 담은 URL을 클릭 → 백엔드에서 유효한 토큰인지 검증 → 성공 시 “비밀번호 재설정 페이지로 이동(또는 API 호출 준비 완료)” 라는 응답을 주는 것
    """
    permission_classes = [AllowAny]

    def get(self,request,uidb64,token):
        """
        토큰/UID 검증만 수행

        uidb64 → user 객체 복원 
        (이메일 링크에 들어있는 uidb64를 디코딩해서 유저 pk를 얻고, 
        그 pk로 db에서 user 객체를 가져오는 것,
        예)uidb64 = "NA==" → 디코딩 → "4" (user.pk = 4))
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Token is valid."}, status=status.HTTP_200_OK)

    def post(self,request):
        """
        본문으로 new_password1, new_password2를 받고 토큰 재검증 후 비밀번호 변경 → JSON 응답
        """
        pass

class AccountSoftDeleteAPIView(APIView):
    def patch(self,request):
        # 비밀번호 확인이 앞서 이루어졌는지 확인(임시)
        if request.headers.get("X-Password-Verified") != "true":
            return Response({
                "error":{
                    "code" : "password_verification_required",
                    "message" : "비밀번호 확인이 필요합니다."
                }
            },status=403)
        success,error_msg = AccountService.account_soft_delete(request.user)
        if success:
            return Response({
                "message": {
                    "code": "account_soft_deleted",
                    "message": "계정이 성공적으로 비활성화되었습니다."
                }
            }, status=200)
        return Response({
            "error": {
                "code": "soft_delete_failed",
                "message": error_msg
            }
        }, status=400)
    
class BlockUserView(APIView):
    """
    유저 차단
    """
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
    """
    차단한 유저 목록 가져오기
    """
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