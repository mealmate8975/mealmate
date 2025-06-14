from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
import re

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)
    
    def validate(self, data):
        user = authenticate(
            request = self.context.get('request'),
            email = data.get("email"),  
            password = data.get("password")
        )
        if not user:
            raise serializers.ValidationError ("이메일 혹은 비밀번호가 일치하지 않습니다.")
        data['user'] = user
        return data
    
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