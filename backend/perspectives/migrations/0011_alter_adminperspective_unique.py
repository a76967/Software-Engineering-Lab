from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('perspectives', '0010_alter_perspective_table'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='adminperspective',
            unique_together={('project',)},
        ),
    ]