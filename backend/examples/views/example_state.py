from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from examples.models import Example, ExampleState
from examples.serializers import ExampleStateSerializer
from projects.permissions import IsProjectMember


class ExampleStateList(generics.ListCreateAPIView):
    serializer_class = ExampleStateSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        return ExampleState.objects.filter(
            example=self.kwargs["example_id"], confirmed_by=self.request.user
        )

    def perform_create(self, serializer):
        queryset = self.get_queryset()
        if queryset.exists():
            queryset.delete()
        else:
            example = get_object_or_404(Example, pk=self.kwargs["example_id"])
            serializer.save(example=example, confirmed_by=self.request.user)
