from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('perspectives', '0005_alter_perspectiveitem_data_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perspectiveitem',
            name='data_type',
            field=models.CharField(max_length=20, choices=[('string','String'), ('number','Number'), ('boolean','Boolean'), ('enum','Enum')]),
        ),
    ]