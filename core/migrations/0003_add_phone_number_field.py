from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_phone_number_to_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Primary contact number', max_length=20, null=True),
        ),
    ]
