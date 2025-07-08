from django.db import IntegrityError
from rest_framework import serializers
from annotation_rules.models import AnnotationRuleGrid, RuleVote, GridVote


class AnnotationRuleGridSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")
    last_edited_by = serializers.ReadOnlyField(source="last_edited_by.username")

    class Meta:
        model = AnnotationRuleGrid
        fields = [
            "id",
            "version",
            "rules",
            "created_by",
            "last_edited_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "project",
            "version",
            "created_by",
            "last_edited_by",
            "created_at",
            "updated_at",
        ]


class RuleVoteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = RuleVote
        fields = ["id", "grid", "rule_index", "value", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def create(self, validated_data):
        user = validated_data.pop("user")
        vote, _ = RuleVote.objects.update_or_create(
            user=user,
            grid=validated_data["grid"],
            rule_index=validated_data["rule_index"],
            defaults={"value": validated_data["value"]},
        )
        return vote


class GridVoteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = GridVote
        fields = ["id", "grid", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]