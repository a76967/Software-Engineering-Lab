from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('perspectives', '0007_adminperspective'),
    ]

    operations = [
        migrations.AddField(
            model_name='perspectiveitem',
            name='admin_perspective',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='perspectives.adminperspective'),
        ),
        migrations.AlterUniqueTogether(
            name='perspectiveitem',
            unique_together={('project', 'admin_perspective', 'name')},
        ),
    ]