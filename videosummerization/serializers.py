from rest_framework import serializers
from session.models import Youtube, YoutubeSummery,TextSummery

class YoutubeSummerySerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeSummery
        fields = '__all__'


class YoutubeSerializer(serializers.ModelSerializer):
    summery= YoutubeSummerySerializer()
    class Meta:
        model = Youtube
        fields = '__all__'


class YoutubeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Youtube
        fields = '__all__'


class TextSummerySerializer(serializers.ModelSerializer):
    class Meta:
        model = TextSummery
        fields = '__all__'