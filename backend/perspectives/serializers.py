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
    def validate(self, attrs):
        if attrs.get('data_type') == 'enum' and not attrs.get('enum'):
            raise serializers.ValidationError({'enum': 'This field is required for enum type.'})
        return attrs

    def create(self, validated_data):
        if 'enum' not in validated_data:
            validated_data['enum'] = []
        return super().create(validated_data)

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
