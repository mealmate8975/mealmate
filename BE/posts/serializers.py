from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','author','page','content','type','image','created_at']
        read_only_fields = ['id','author','created_at']
        
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("내용은 공백일 수 없습니다.")
        return value    