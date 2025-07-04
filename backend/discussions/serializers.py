from rest_framework import serializers
from .models import Discussion, DiscussionSession

class DiscussionSerializer(serializers.ModelSerializer):
    senderId = serializers.IntegerField(source='user.id', read_only=True)
    senderName = serializers.CharField(source='user.username', read_only=True)
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    session = serializers.IntegerField(required=False)

    class Meta:
        model = Discussion
        fields = ['id', 'text', 'senderId', 'senderName', 'timestamp', 'session']


class DiscussionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionSession
        fields = ['id', 'number']
        read_only_fields = ['number']