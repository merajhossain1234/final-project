from rest_framework import serializers
from session.models import Youtube, YoutubeSummery

class YoutubeSummerySerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeSummery
        fields = '__all__'


class YoutubeSerializer(serializers.ModelSerializer):
    summery= YoutubeSummerySerializer()
    class Meta:
        model = Youtube
        fields = '__all__'




