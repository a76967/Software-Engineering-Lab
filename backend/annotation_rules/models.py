from django.conf import settings
from django.db import models
from django.db.models import JSONField

class AnnotationRuleGrid(models.Model):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='annotation_rule_grids'
    )
    version = models.PositiveIntegerField()
    rules = JSONField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'version')
        ordering = ['-project', '-version']

    def save(self, *args, **kwargs):
        if not self.pk:
            last = AnnotationRuleGrid.objects.filter(
                project=self.project
            ).order_by('-version').first()
            self.version = (last.version if last else 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.name} – Rules v{self.version}"


class RuleVote(models.Model):
    VALUE_CHOICES = [
        ("up", "Thumbs Up"),
        ("down", "Thumbs Down"),
    ]

    grid = models.ForeignKey(
        AnnotationRuleGrid,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    rule_index = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )
    value = models.CharField(max_length=4, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("grid", "rule_index", "user")

    def __str__(self):
        return f"Vote {self.value} by {self.user} on grid {self.grid_id} rule {self.rule_index}"