# BE/accounts/accounts_service.py

# import logging
# from django.core.mail import EmailMultiAlternatives  # HTML 메일까지 고려 시
import re
from django.utils import timezone
from datetime import timedelta
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import BadHeaderError
import socket
from smtplib import (
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPServerDisconnected,
    SMTPException,
)
from django.urls import NoReverseMatch
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from urllib.parse import urlencode
from django.shortcuts import redirect
from rest_framework.response import Response

from .serializers import (
    PasswordResetConfirmSerializer,
) 

from .models import UserBlock

User = get_user_model()
# logger = logging.getLogger(__name__)

class AccountService:
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
    
    def verify_email(self,request,uidb64, token):
        """
        이메일 인증 검증 로직
        """
        # uidb64 디코딩, 사용자 조회, 토큰 검증, email_verified 갱신
        
        # 1) uid → user 조회
        try:
            # uidb64 복호화 → 사용자 조회
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            return self._respond(request,"invalid_uid","잘못된 사용자 식별입니다.",400)
        except User.DoesNotExist:
            return self._respond(request,"user_not_found","해당 사용자를 찾을 수 없습니다.",404)
        
        # 2) 이미 인증된 계정
        if getattr(user,"email_verified",False):
            return self._respond(request,"already_verified","이미 이메일 인증이 완료되었습니다.",200)
        
        # 3) 토큰 검증
        if not default_token_generator.check_token(user,token): # default_token_generator.check_token(user, token) 검증
            return self._respond(request,"invalid_or_expired_token","토큰이 유효하지 않거나 만료되었습니다.",400)
        
        # 4) 인증 처리
        user.email_verified = True # 성공 시 email_verified=True 저장
        user.save(update_fields=["email_verified"])
        return self._respond(request,"verify_success","이메일 인증이 완료되었습니다.",200)
        
    @staticmethod
    def validate_uid_and_token(uidb64, token):
        """
        UID/Token 검증 전용 헬퍼
        Returns:
            (success: bool, code: str, message: str, status: int, user: Optional[User])
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            return False, "INVALID_UID", "유효하지 않은 UID입니다.", 400, None
        except User.DoesNotExist:
            return False, "USER_NOT_FOUND", "해당 사용자를 찾을 수 없습니다.", 404, None

        if not default_token_generator.check_token(user, token):
            return False, "INVALID_TOKEN", "유효하지 않은 토큰 또는 만료된 토큰입니다.", 400, None

        return True, "VALID", "유효한 토큰입니다.", 200, user
    
    @staticmethod
    def confirm_reset_password(uidb64:str,token:str,data) -> tuple[bool,str,str,int]:
        """
        비밀번호 재설정 로직
        Returns: (success, code, message, http_status)
        """
        # 1) UID/토큰 검증 (실패 시 즉시 반환)
        success,code,message,status,user = AccountService.validate_uid_and_token(uidb64, token)
        if not success:
            return False, code, message, status

        # 2) 시리얼라이저 검증 (실패 시 즉시 반환)
        serializer = PasswordResetConfirmSerializer(data=data,context={"user":user})
        if not serializer.is_valid():
            # 에러 메시지 안전 추출
            # errors는 {"new_password2": ["두 비밀번호는 일치하지 않습니다."]} 형태가 일반적
            first_key = next(iter(serializer.errors))
            first_error = serializer.errors[first_key]
            # first_error가 리스트/문자열인 경우를 커버
            if isinstance(first_error, (list,tuple)) and first_error:
                message_text = str(first_error[0])
            else:
                message_text = str(first_error)
            
            return False, "validation_error", message_text, 400

        # 3) 성공 시에만 저장
        new_password = serializer.validated_data['new_password1']
        user.set_password(new_password)
        user.save(update_fields=["password"])

        return True, "password_reset_success", "비밀번호가 재설정되었습니다.", 200
    
    @staticmethod
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

    @staticmethod
    def patch_my_info(user,data):
        """
        회원정보 수정 (비밀번호 변경은 APIView에 따로 구현)
        """
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
    
    # last_login is null 케이스 대비 :
    # 가입 후  한 번도 로그인하지 않은 유저는 last_login = None일 수 있으므로

    @staticmethod
    def account_soft_delete(user):
        """
        회원 탈퇴 요청 로직
        """
        if not user.is_active:
            return False, "이미 비활성화된 유저입니다."  # 이미 비활성화된 유저

        try:
            user.is_active = False
            user.withdrawn_at = timezone.now()
            user.save()
            return True, None
        except Exception as e:
            # logger.error(f"탈퇴 처리 중 예외 발생: {str(e)}")
            return False, "계정 비활성화 중 예기치 못한 오류가 발생했습니다."

    @staticmethod
    def activate_account(user):
        """
        휴면 또는 탈퇴 유예 상태였던 유저를 재활성화
        """
        if user.is_active:
            return False, None  # 이미 활성화된 유저
        
        if user.withdrawn_at:
            reason = "withdrawn_cancellation"
        else:
            reason = "dormant_wakeup"

        try:
            user.is_active = True
            user.withdrawn_at = None
            user.save()
            return True, reason
        except Exception:
            return False, None

    @staticmethod
    def deactivate_dormant_users():
        """
        1년 이상 미접속 유저 휴면 처리 로직
        """
        threshold = timezone.now() - timedelta(days=365)
        User.objects.filter(
            is_active=True,
            last_login__isnull=False,
            last_login__lte=threshold
        ).update(is_active=False)

    @staticmethod
    def delete_soft_deleted_accounts():
        """
        삭제 유예기간이 끝난 유저 삭제 로직
        """
        try:
            threshold = timezone.now() - timedelta(days=30)
            delete_target = User.objects.filter(
                is_active=False,
                withdrawn_at__isnull=False,
                withdrawn_at__lte=threshold
                )
            cnt, _ = delete_target.delete()
            return {"status": "ok", "deleted_count": cnt}
        except Exception as e:
            # logger.error(f"[유저 삭제 실패] 예외 발생: {str(e)}", exc_info=True)  # 로깅은 추후 사용
            return {"status": "error", "deleted_count": 0}
    
    @staticmethod
    def send_verification_email(user,request): # class VerifyEmailAPIView(APIView):
        """
        인증 메일 발송(회원가입 직후 호출)
        동작: 사용자가 메일 링크 클릭 → 백엔드 뷰가 직접 토큰 검증 → 결과에 따라 프론트로 리다이렉트(성공/실패 코드 포함)
        """
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        try:
            # reverse()를 사용하여 'accounts:verify-email' URL 패턴의 상대 경로 생성
            # kwargs로 uidb64(유저 PK를 base64로 인코딩한 값)와 token(이메일 인증 토큰)을 전달
            # 예: "/accounts/verify-email/MjE/abc123token/"
            relative_url = reverse('accounts:verify-email',kwargs={'uidb64':uidb64,'token':token})

            # request.build_absolute_uri()를 사용하여 현재 요청의 도메인과 상대 경로를 결합해 절대 URL 생성
            # 예: "https://example.com/accounts/verify-email/MjE/abc123token/"
            # 이렇게 만든 URL을 이메일 본문에 넣어 사용자가 클릭하면 인증 뷰로 접근 가능
            verify_url = request.build_absolute_uri(relative_url) # 결과 화면 UX를 프론트에서 풍부하게 보여주려면 검증 후 리다이렉트 처리가 추가로 필요
            # 이후 UX를 풍부하게 하고 싶을 때 SPA 방식으로 전환/병행(이때는 이메일 링크를 프론트로 보내고, 프론트에서 검증 API 호출)

            subject = "[Mealmate] 이메일 인증 안내"
            msg_txt = f"Mealmate 가입을 환영합니다! \n 아래 링크를 2시간 이내에 클릭해 이메일 인증을 완료해 주세요.\n {verify_url}\n 본인이 요청하지 않았다면 이 메일을 무시하셔도 됩니다."
            # 발송함수 호출
            send_mail(subject,msg_txt,settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=False)
            return True, None
        except BadHeaderError as e: # 메일 헤더/포맷 오류 (개발 실수 계열)
            # logger.warning("Bad header", extra=...)
            return False, "메일 헤더가 유효하지 않아 발송에 실패했습니다."
        except (SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected, SMTPException, TimeoutError, socket.gaierror) as e:
            # SMTP 인증/연결 문제 (환경 설정/인프라 계열)
            # logger.error("SMTP error", extra=...)
            return False, "이메일 서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        except NoReverseMatch as e: # URL 생성/리버스 실패 (라우팅 설정 계열)
            # logger.error("URL reverse error", extra=...)
            return False, "인증 링크 생성 중 오류가 발생했습니다."
        except ValueError as e: # 이메일 주소 문제(입력 데이터 계열)
            # logger.warning("Invalid email", extra=...)
            return False, "이메일 주소가 유효하지 않아 발송할 수 없습니다."
        except Exception as e:
            # logger.error("Unknown error", extra=...)
            return False, "인증 메일 발송 중 예기치 못한 오류가 발생했습니다."
        
    @staticmethod
    def reset_password(email:str,request):
        """
        비밀번호 재설정
        이메일 기입 시 인증 메일 발송 → 사용자가 메일 링크 클릭 → 백엔드 뷰가 직접 토큰 검증 → 성공 시 비밀번호 재설정 화면으로 이동
        """
        # 1) 사용자 조회 (존재 노출 방지)
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return {"code": "NOT_FOUND_NOOP"}                           # 사용자 미존재 (아무 작업도 안 했음, 정상 흐름)
        
        # 2) uid/token 생성
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        try:
            # 3) password reset URL 생성
            relative_url = reverse('accounts:password-reset',kwargs={'uidb64':uidb64,'token':token})
            reset_url = request.build_absolute_uri(relative_url)
           
            # 4) 메일 발송 (비밀번호 재설정 문구)
            subject = "[Mealmate] 비밀번호 재설정"
            msg_txt = f"비밀번호 재설정을 요청하셨습니다.\n 아래 링크를 30분 이내에 클릭하여 새 비밀번호를 설정해 주세요.\n {reset_url}\n 본인이 요청하지 않았다면 이 메일을 무시해 주세요."
            # 발송함수 호출
            send_mail(subject,msg_txt,settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=False)
            return {"code": "FOUND_SENT"}                               # 사용자 존재 + 메일 발송 시도 성공
        except BadHeaderError: # 메일 헤더/포맷 오류 (개발 실수 계열)
            # logger.warning("Bad header", extra=...)
            return {"code": "SEND_FAILED", "reason": "bad_header"}      # 헤더 오류
        except (SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected, SMTPException, TimeoutError, socket.gaierror):
            # SMTP 인증/연결 문제 (환경 설정/인프라 계열)
            # logger.error("SMTP error", extra=...)
            return {"code": "SEND_FAILED", "reason": "smtp"}            # SMTP/네트워크 등 발송 실패
        except NoReverseMatch: # URL 생성/리버스 실패 (라우팅 설정 계열)
            # logger.error("URL reverse error", extra=...)
            return {"code": "SEND_FAILED", "reason": "reverse"}         # URL reverse 실패
        except Exception:
            return {"code": "SEND_FAILED", "reason": "unknown"}     # 기타 예외

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
                    "error": {
                        "code": "self_block",
                        "message": "자기 자신을 차단할 수 없습니다."
                    }
                }, 400
            relation_qs = UserBlock.objects.filter(blocker=blocker, blocked_user=blocked_user)
            if relation_qs.exists():
                return {
                    "error": {
                        "code": "already_blocked",
                        "message": "이미 차단된 유저입니다."
                    }
                }, 400
            
            relation_qs.create(blocker=blocker, blocked_user=blocked_user)
            return {
                "message": "유저가 차단되었습니다."
            }, 200
            
        except User.DoesNotExist:
            return {
                "error": {
                    "code": "user_not_found",
                    "message": "존재하지 않는 유저는 차단할 수 없습니다."
                }
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
        
    @staticmethod
    def get_blocked_user(user):
        try:
            blocked_users = UserBlock.objects.filter(blocker=user).select_related('blocked_user')
            return {
                "blocked_users":[
                    {
                        "name": b.blocked_user.name,
                        "nickname" : b.blocked_user.nickname,
                        "gender" : b.blocked_user.gender,
                    }
                    for b in blocked_users
                ]
            }, 200
        except Exception as e:
            return {
                "error": {
                    "code": "blocked_list_failed",
                    "message": "차단 목록 조회 중 오류가 발생했습니다."
                }
            }, 500