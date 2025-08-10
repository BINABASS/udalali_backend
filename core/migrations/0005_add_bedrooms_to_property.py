from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_status_to_property'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='bedrooms',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
