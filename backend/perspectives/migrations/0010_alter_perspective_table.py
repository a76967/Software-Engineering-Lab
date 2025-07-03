from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("perspectives", "0009_perspective_admin_perspective"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="perspective",
            table="perspectives_userperspective",
        ),
    ]