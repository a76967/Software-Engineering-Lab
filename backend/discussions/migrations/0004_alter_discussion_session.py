# Generated by Django 4.2.19 on 2025-07-04 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discussions', '0003_discussionsession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='session',
            field=models.IntegerField(default=1),
        ),
    ]
