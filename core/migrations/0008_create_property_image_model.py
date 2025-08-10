from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_create_property_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='property_images/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('is_primary', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-is_primary', 'created_at'],
            },
        ),
        migrations.AddField(
            model_name='propertyimage',
            name='property',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='images', to='core.property'),
        ),
    ]
