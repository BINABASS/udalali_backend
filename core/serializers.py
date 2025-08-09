# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, Subscription, Transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'user_type', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_verified': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'user_type', 'password', 'password2']
        extra_kwargs = {
            'user_type': {'default': 'BUYER'},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class PropertySerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    seller_details = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'seller', 'seller_details', 'title', 'description', 'price', 
            'formatted_price', 'location', 'property_type', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'seller']

    def get_seller_details(self, obj):
        return {
            'id': obj.seller.id,
            'username': obj.seller.username,
            'phone': obj.seller.phone
        }

    def get_formatted_price(self, obj):
        return f"${obj.price:,.2f}"

class SubscriptionSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='SELLER'))
    formatted_price = serializers.SerializerMethodField()
    active_status = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'seller', 'plan_name', 'price', 'formatted_price',
            'start_date', 'end_date', 'active_status'
        ]

    def get_formatted_price(self, obj):
        return f"${obj.price:,.2f}"

class TransactionSerializer(serializers.ModelSerializer):
    buyer = serializers.PrimaryKeyRelatedField(read_only=True)
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.filter(is_available=True))
    formatted_amount = serializers.SerializerMethodField()
    transaction_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    buyer_details = serializers.SerializerMethodField()
    property_details = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'buyer', 'buyer_details', 'property', 'property_details',
            'amount', 'formatted_amount', 'transaction_date', 'status',
            'payment_reference'
        ]
        read_only_fields = ['transaction_date', 'status']

    def get_formatted_amount(self, obj):
        return f"${obj.amount:,.2f}"

    def get_buyer_details(self, obj):
        return {
            'id': obj.buyer.id,
            'username': obj.buyer.username,
            'phone': obj.buyer.phone
        }

    def get_property_details(self, obj):
        return {
            'id': obj.property.id,
            'title': obj.property.title,
            'price': obj.property.price,
            'location': obj.property.location
        }

    def validate(self, data):
        if self.instance:
            if self.instance.status != 'PENDING':
                raise serializers.ValidationError("Cannot modify a completed transaction")
        return data

class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'property_type']

class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'property_type', 'is_available']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'price': {'required': False},
            'location': {'required': False},
            'property_type': {'required': False},
        }

class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        token = data.get('token')
        if not token:
            raise serializers.ValidationError("Token is required")
        return data

    def create(self, validated_data):
        return validated_data