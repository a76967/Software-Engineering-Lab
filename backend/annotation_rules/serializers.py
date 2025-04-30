from rest_framework import serializers
from .models import AnnotationRuleGrid

class AnnotationRuleGridSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")
    last_edited_by = serializers.ReadOnlyField(source="last_edited_by.username")

    class Meta:
        model = AnnotationRuleGrid
        fields = [
            "id",
            "project",
            "version",
            "rules",
            "created_by",
            "last_edited_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "version",
            "created_by",
            "last_edited_by",
            "created_at",
            "updated_at",
        ]