from rest_framework import generics, permissions
from .models import Discussion
from .serializers import DiscussionSerializer

class DiscussionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Discussion.objects.filter(project_id=self.kwargs['project_id'])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            project_id=self.kwargs['project_id']
        )

class DiscussionDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'discussion_id'

    def get_queryset(self):
        return Discussion.objects.filter(project_id=self.kwargs['project_id'])