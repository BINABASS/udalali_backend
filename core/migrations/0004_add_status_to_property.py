from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_status_to_property'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('pending', 'Pending'), ('sold', 'Sold')], default='available', max_length=20),
        ),
    ]
