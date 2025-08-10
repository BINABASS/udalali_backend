from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, Subscription, Transaction, PropertyImage
from .PropertyImageSerializer import PropertyImageSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'user_type', 'role', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['date_joined', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_role(self, obj):
        return obj.user_type.lower()

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class PropertySerializer(serializers.ModelSerializer):
    seller_id = serializers.PrimaryKeyRelatedField(
        source='seller',
        queryset=User.objects.all(),
        write_only=True
    )
    seller = UserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    formatted_price = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=Property.STATUS_CHOICES, required=False)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'price', 'formatted_price',
            'location', 'property_type', 'status', 'bedrooms', 'bathrooms',
            'area', 'amenities', 'is_available', 'seller', 'seller_id',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'seller']

    def get_formatted_price(self, obj):
        return obj.formatted_price

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'property', 'notify_on_updates', 'created_at']
        read_only_fields = ['user', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'property', 'buyer', 'seller', 'amount', 'status',
            'payment_reference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'seller', 'created_at', 'updated_at']

class CustomTokenObtainPairSerializer(serializers.Serializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
