from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0009_annotationrulegrid"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="root_project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="versions",
                to="projects.project",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="version_number",
            field=models.PositiveIntegerField(default=1),
        ),
    ]