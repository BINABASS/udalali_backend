from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_bedrooms_to_property'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='bathrooms',
            field=models.DecimalField(decimal_places=1, max_digits=3, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='property',
            name='area',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='property',
            name='amenities',
            field=models.JSONField(default=list, blank=True),
        ),
    ]
