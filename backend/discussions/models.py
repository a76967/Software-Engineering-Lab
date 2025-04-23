from django.db import models
from django.conf import settings
from projects.models import Project

class Discussion(models.Model):
    project = models.ForeignKey(Project, related_name='discussions', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='discussions', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']