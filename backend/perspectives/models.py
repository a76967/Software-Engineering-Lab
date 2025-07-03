from django.db import models
from django.conf import settings
from projects.models import Project
from django.db.models import JSONField


class Perspective(models.Model):
    CATEGORY_CHOICES = [
        ("cultural", "Cultural"),
        ("technic", "Technic"),
        ("subjective", "Subjective"),
    ]

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default="Default Subject")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="subjective")
    text = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="perspectives")
    linkedAnnotations = JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class PerspectiveItem(models.Model):
    TYPE_CHOICES = [
        ("string", "String"),
        ("number", "Number"),
        ("boolean", "Boolean"),
        ("enum", "Enum"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="perspective_items",
    )
    admin_perspective = models.ForeignKey(
        "AdminPerspective",
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("project", "admin_perspective", "name")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.project_id}: {self.name}"

class AdminPerspective(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="admin_perspectives")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return self.name