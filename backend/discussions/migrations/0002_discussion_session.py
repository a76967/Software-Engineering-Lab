from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('discussions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussion',
            name='session',
            field=models.IntegerField(default=1),
        ),
    ]