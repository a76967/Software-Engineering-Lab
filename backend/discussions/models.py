from django.db import models
from django.conf import settings
from projects.models import Project

class Discussion(models.Model):
    project = models.ForeignKey(Project, related_name='discussions', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='discussions', on_delete=models.CASCADE)
    session = models.IntegerField(default=1)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class DiscussionSession(models.Model):
    project = models.ForeignKey(Project, related_name='discussion_sessions', on_delete=models.CASCADE)
    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'number')
        ordering = ['number']

    def __str__(self) -> str:
        return f"{self.project_id}-session-{self.number}"