from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0008_project_allow_member_to_create_label_type_and_more"),
        ("perspectives", "0003_perspective_linkedannotations"),
    ]

    operations = [
        migrations.CreateModel(
            name="PerspectiveItem",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("data_type", models.CharField(max_length=20)),
                ("required", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="perspective_items",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.AlterUniqueTogether(
            name="perspectiveitem",
            unique_together={("project", "name")},
        ),
    ]