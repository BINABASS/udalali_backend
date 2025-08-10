from rest_framework import serializers
from .models import PropertyImage

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']
        read_only_fields = ['created_at']
