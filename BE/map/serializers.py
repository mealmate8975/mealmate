from rest_framework import serializers

class ScheduleLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=True)
    lng = serializers.FloatField(required=True)

class RealTimeLocationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    lat = serializers.FloatField(allow_null=True)
    lng = serializers.FloatField(allow_null=True)