# BE/accounts/views.py

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RegisterSerializer
from .accounts_service import AccountService,BlockUserService

User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = AccountService.register(validated_data)
            return Response({"message": "회원가입 성공",},status=201)
        return Response(serializer.errors,status=400)

class LoginAPIView(APIView):
    def post(self, request):
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
        
        error_message = serializer.errors.get('non_field_errors', ["로그인 실패"])[0]
        return Response({
            "error": {
                "code": "invalid_credentials",
                "message": error_message
            }
            }, status=400)

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
        return Response({"error":error_msg},status_code=status_code)

# 차단
class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        data,status_code = BlockUserService.block_user(request.user, user_id)
        return Response(data,status=status_code)

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