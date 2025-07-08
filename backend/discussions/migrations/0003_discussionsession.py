from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_annotationrulegrid'),
        ('discussions', '0002_discussion_session'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscussionSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='discussion_sessions',
                        to='projects.project',
                    ),
                ),
            ],
            options={
                'ordering': ['number'],
                'unique_together': {('project', 'number')},
            },
        ),
    ]