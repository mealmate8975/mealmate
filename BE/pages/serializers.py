from rest_framework import serializers
from .models import Page

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id','name','description','created_at']
        read_only_fields = ['id','created_at']
    def validate_name(self,value):
        if not value.strip():
            raise serializers.ValidationError("페이지 이름은 공백일 수 없습니다.")
        return value
    def validate_description(self,value):
        if value is not None and not isinstance(value,dict):
            raise serializers.ValidationError("description은 JSON 객체여야 합니다.")
        return value