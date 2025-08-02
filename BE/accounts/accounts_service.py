# BE/accounts/accounts_service.py

from django.contrib.auth import get_user_model

User = get_user_model()

class AccountService():
    def register(validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            phone=validated_data["phone"],
            nickname=validated_data["nickname"],
            gender=validated_data["gender"]
        )