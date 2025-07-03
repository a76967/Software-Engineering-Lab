from rest_framework import serializers
from .models import Perspective, PerspectiveItem, AdminPerspective

class PerspectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perspective
        fields = '__all__'
        extra_kwargs = {
            'linkedAnnotations': {'read_only': False},
            'project': {'read_only': True},
            'admin_perspective': {'required': False, 'allow_null': True},
        }

class PerspectiveItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveItem
        fields = '__all__'
        extra_kwargs = {
            'order': {'required': False},
            'project': {'read_only': True},
            'admin_perspective': {'required': False, 'allow_null': True},
        }

class AdminPerspectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPerspective
        fields = '__all__'
        extra_kwargs = {
            'project': {'read_only': True},
            'user': {'read_only': False}
        }
