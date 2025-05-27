from .models import Schedules
from rest_framework import serializers

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedules
        fields = [
            'schedule_id',
            'rest_id',
            'created_by',
            'schedule_name',
            'created_at',
            'schedule_at',
            'schedule_condition'
        ]

        # 서버가 자동으로 할당합니다. 뷰에서 request.user로 해놔서 자동으로 로그인한 유저가 생성자가 됩니다.
        read_only_fields = ['created_by']
