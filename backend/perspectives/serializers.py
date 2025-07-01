from rest_framework import serializers
from .models import Perspective, PerspectiveItem


class PerspectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perspective
        fields = "__all__"
        extra_kwargs = {
            "linkedAnnotations": {"read_only": False},
        }


class PerspectiveItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveItem
        fields = "__all__"
