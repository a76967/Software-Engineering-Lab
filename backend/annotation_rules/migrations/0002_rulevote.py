from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotation_rules', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RuleVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_index', models.PositiveIntegerField()),
                ('value', models.CharField(choices=[('up', 'Thumbs Up'), ('down', 'Thumbs Down')], max_length=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('grid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='annotation_rules.annotationrulegrid')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('grid', 'rule_index', 'user')},
            },
        ),
    ]