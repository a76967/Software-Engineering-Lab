from rest_framework import viewsets, permissions
from .models import AnnotationRuleGrid, RuleVote, GridVote
from .serializers import (
    AnnotationRuleGridSerializer,
    RuleVoteSerializer,
    GridVoteSerializer,
)

class AnnotationRuleGridViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnnotationRuleGridSerializer

    def get_queryset(self):
        pid = self.kwargs["project_pk"]
        return AnnotationRuleGrid.objects.filter(project__pk=pid)

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_pk"],
            created_by=self.request.user,
            last_edited_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(last_edited_by=self.request.user)


class RuleVoteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RuleVoteSerializer

    def get_queryset(self):
        pid = self.kwargs["project_pk"]
        return RuleVote.objects.filter(grid__project__pk=pid)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GridVoteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GridVoteSerializer

    def get_queryset(self):
        pid = self.kwargs["project_pk"]
        return GridVote.objects.filter(grid__project__pk=pid)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)