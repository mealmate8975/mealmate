# BE/accounts/accounts_service.py

import re
from django.utils import timezone
from datetime import timedelta
# import logging
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
# from django.core.mail import EmailMultiAlternatives  # HTML 메일까지 고려 시
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
from django.shortcuts import get_object_or_404

from .models import UserBlock

User = get_user_model()
# logger = logging.getLogger(__name__)

class AccountService:
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
    def send_reset_password_email(email,request):
        """
        비밀번호 초기화
        이메일 기입 시 인증 메일 발송 → 사용자가 메일 링크 클릭 → 백엔드 뷰가 직접 토큰 검증 → 성공 시 비밀번호 초기화, 비밀번호 재설정 화면으로 이동
        """
        # 1) 사용자 조회 (존재 노출 방지)
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return True, None # 존재하지 않아도 "성공"으로 처리
        
        # 2) uid/token 생성
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        try:
            # 3) reset confirm URL 생성
            relative_url = reverse('accounts:password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            reset_url = request.build_absolute_uri(relative_url)
           
            # 4) 메일 발송 (비밀번호 재설정 문구)
            subject = "[Mealmate] 비밀번호 초기화"
            msg_txt = f"비밀번호 재설정을 요청하셨습니다.\n 아래 링크를 30분 이내에 클릭하여 새 비밀번호를 설정해 주세요.\n {reset_url}\n 본인이 요청하지 않았다면 이 메일을 무시해 주세요."
            # 발송함수 호출
            send_mail(subject,msg_txt,settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=False)
            return True, None
        except BadHeaderError: # 메일 헤더/포맷 오류 (개발 실수 계열)
            # logger.warning("Bad header", extra=...)
            return False, "메일 헤더가 유효하지 않아 발송에 실패했습니다."
        except (SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected, SMTPException, TimeoutError, socket.gaierror):
            # SMTP 인증/연결 문제 (환경 설정/인프라 계열)
            # logger.error("SMTP error", extra=...)
            return False, "이메일 서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        except NoReverseMatch: # URL 생성/리버스 실패 (라우팅 설정 계열)
            # logger.error("URL reverse error", extra=...)
            return False, "재설정 링크 생성 중 오류가 발생했습니다."
        except Exception:
            return False, "비밀번호 재설정 메일 발송 중 예기치 못한 오류가 발생했습니다."

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