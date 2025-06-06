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
            'schedule_start',
            'schedule_end',
            'is_meal',
            'schedule_condition'
        ]
        
    def validate(self, data):
        schedule_start = data.get("schedule_start", getattr(self.instance, "schedule_start", None))
        schedule_end = data.get("schedule_end", getattr(self.instance, "schedule_end", None))

        # 둘 다 존재하는 경우에만 순서 비교
        if schedule_start is not None and schedule_end is not None:
            if schedule_end < schedule_start:
                raise serializers.ValidationError("종료 시간이 시작 시간보다 빠를 수 없습니다.")

        return data
