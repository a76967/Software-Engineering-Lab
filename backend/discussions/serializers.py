from rest_framework import serializers
from .models import Discussion

class DiscussionSerializer(serializers.ModelSerializer):
    senderId = serializers.IntegerField(source='user.id', read_only=True)
    senderName = serializers.CharField(source='user.username', read_only=True)
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Discussion
        fields = ['id', 'text', 'senderId', 'senderName', 'timestamp']