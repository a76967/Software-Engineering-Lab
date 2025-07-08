from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('perspectives', '0008_perspectiveitem_admin_perspective'),
    ]

    operations = [
        migrations.AddField(
            model_name='perspective',
            name='admin_perspective',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perspectives', to='perspectives.adminperspective'),
        ),
    ]