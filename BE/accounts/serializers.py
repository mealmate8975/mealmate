# BE/accounts/serializers.py

from rest_framework import serializers
from .models import CustomUser
import re
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self,value):
        value = value.strip() # 공백 제거
        value = User.objects.normalize_email(value) # @뒤의 문자들만 모두 소문자로 바꿈
        return value

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only = True)
    phone = serializers.CharField(required=False)
    nickname = serializers.CharField()
    gender = serializers.ChoiceField(choices=[('0', 'Male'), ('1', 'Female')])

    def validate(self, data):
        email = data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("이미 등록된 이메일입니다.")
        return data
    
    def validate_phone(self, data):
        if not re.match(r'010\d{8}$',data):
            raise serializers.ValidationError("전화번호 형식 오류")
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)
    
    def validate(self, data):
        user = authenticate(
            request = self.context.get('request'),
            username = data.get("email"),  
            password = data.get("password")
        )
        if not user:
            raise serializers.ValidationError ("이메일 혹은 비밀번호가 일치하지 않습니다.")
        data['user'] = user
        return data

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
    def validate_old_password(self, value):
        """
        기존 비밀번호 확인
        """
        user = self.context['request'].user
        if not user.check_password(value): # check_password : 일치하면 True, 아니면 False를 반환
            raise serializers.ValidationError("기존 비밀번호가 일치하지 않습니다.")
        return value
    
    def validate_new_password(self, value):
        user = self.context['request'].user # self.context['request'].user는 현재 요청을 보낸 로그인된 사용자 객체
        try:
            password_validation.validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

class PasswordVerifySerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self,value):
        user = self.context['request'].user # self.context['request'].user는 현재 요청을 보낸 로그인된 사용자 객체
        if not user.check_password(value):
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.", code="incorrect_password")
        return value

# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.exceptions import AuthenticationFailed
    
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     username_field = 'email'

#     def validate(self, attrs):
#         # email과 password를 받아서 직접 매핑
#         email = attrs.get("email")
#         password = attrs.get("password")

#         user = authenticate(username=email, password=password)

#         if user is None:
#             raise AuthenticationFailed('이메일 또는 비밀번호가 올바르지 않습니다')

#         refresh = self.get_token(user)

#         return {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }