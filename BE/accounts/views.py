from .serializers import LoginSerializer, RegisterSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from .models import CustomUser



class LoginView(APIView):
    def get(self, request):
        # 로그인 페이지를 렌더링
        return render(request, 'login.html')
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({"message": "로그인 성공", "nickname": user.nickname}, status=200)
        return Response(serializer.errors, status=400)
    
class RegisterView(APIView):
    def get(self, request):
        # 회원가입 페이지를 렌더링
        return render(request, 'register.html')
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                email = serializer.validated_data['email'],
                name = serializer.validated_data['name'],
                password = serializer.validated_data['password'],
                phone = serializer.validated_data['phone'],
                nickname = serializer.validated_data['nickname']
            )
            return Response({
                "message": "회원가입 성공", 'USER_ID': user.email
            }, status=201)
        return Response(serializer.errors, status=400)