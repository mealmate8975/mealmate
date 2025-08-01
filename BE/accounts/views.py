from .serializers import LoginSerializer, RegisterSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from .models import UserBlock
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = CustomUser.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                name=validated_data["name"],
                phone=validated_data.get("phone", ""),
                nickname=validated_data["nickname"],
                gender=validated_data["gender"]
            )
            return Response({
                "message": "회원가입 성공",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "name": user.name,
                    "gender": user.gender,
                    "phone": user.phone
                }
            }, status=201)
        return Response(serializer.errors, status=400)

# @method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    def post(self, request):
        # print("request.data:", request.data)
        # print("request.body:", request.body)
        
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "name": user.name,
                    "gender": user.gender,
                    "phone": user.phone
                }
            }, status=200)
        # print("serializer.errors:", serializer.errors)
        error_message = serializer.errors.get('non_field_errors', ["로그인 실패"])[0]
        return Response({
            "error": {
                "code": "invalid_credentials",
                "message": error_message
            }
            }, status=400)
        # return Response(serializer.errors, status=400)

class UserMeView(APIView):
    permission_classes = [IsAuthenticated]  # JWT 토큰 필요

    def get(self, request):
        user = request.user  # JWT 토큰에서 복원된 유저
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
    
# from .serializers import MyTokenObtainPairSerializer

# class RegisterView(APIView):
#     def get(self, request):
#         # 회원가입 페이지를 렌더링
#         return render(request, 'register.html')
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = CustomUser.objects.create_user(
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