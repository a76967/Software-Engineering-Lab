from rest_framework import generics, permissions
from .models import Discussion, DiscussionSession
from .serializers import DiscussionSerializer, DiscussionSessionSerializer

class DiscussionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Discussion.objects.filter(project_id=self.kwargs['project_id'])
        session = self.request.query_params.get('session', '1')
        return qs.filter(session=session)

    def perform_create(self, serializer):
        session = (
            self.request.data.get('session')
            or self.request.query_params.get('session')
            or 1
        )
        DiscussionSession.objects.get_or_create(
            project_id=self.kwargs['project_id'],
            number=session,
        )
        serializer.save(
            user=self.request.user,
            project_id=self.kwargs['project_id'],
            session=session,
        )

class DiscussionDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'discussion_id'

    def get_queryset(self):
        qs = Discussion.objects.filter(project_id=self.kwargs['project_id'])
        session = self.request.query_params.get('session', '1')
        return qs.filter(session=session)


class DiscussionSessionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DiscussionSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiscussionSession.objects.filter(
            project_id=self.kwargs['project_id']
        ).order_by('number')

    def perform_create(self, serializer):
        existing = DiscussionSession.objects.filter(
            project_id=self.kwargs['project_id']
        ).order_by('-number').first()
        next_number = existing.number + 1 if existing else 1
        serializer.save(project_id=self.kwargs['project_id'], number=next_number)