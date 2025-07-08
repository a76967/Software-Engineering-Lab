from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('perspectives', '0012_alter_adminperspective_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='perspectiveitem',
            name='enum',
            field=models.JSONField(blank=True, default=list),
        ),
    ]