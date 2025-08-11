from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage, Booking, Message, Report
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

class BookingSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'property_title', 'user', 'user_name', 
            'start_date', 'end_date', 'status', 'total_price', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'recipient', 'recipient_name',
            'property', 'property_title', 'message_type', 'subject', 'content',
            'is_read', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sender', 'is_read', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True, allow_null=True)
    reported_user_name = serializers.CharField(source='reported_user.get_full_name', read_only=True, allow_null=True)
    reported_property_title = serializers.CharField(source='reported_property.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'report_type', 'title', 'description', 'reported_by', 'reported_by_name',
            'reported_user', 'reported_user_name', 'reported_property', 'reported_property_title',
            'status', 'resolution_notes', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reported_by', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']


class CustomTokenObtainPairSerializer(serializers.Serializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
