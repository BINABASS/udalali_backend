from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage, Booking, Message, Report
from .PropertyImageSerializer import PropertyImageSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'user_type', 'role', 'is_verified', 'date_joined',
            'is_staff', 'is_superuser', 'last_login'
        ]
        read_only_fields = ['date_joined', 'is_verified', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_role(self, obj):
        # Return the user_type in lowercase for frontend compatibility
        return obj.user_type.lower() if obj.user_type else 'customer'

    def to_representation(self, instance):
        # Ensure consistent output format
        representation = super().to_representation(instance)
        # Make sure role is always included and matches user_type
        representation['role'] = self.get_role(instance)
        return representation

    def create(self, validated_data):
        # Handle user creation with proper defaults
        user_type = validated_data.get('user_type', User.USER_TYPE_CHOICES[0][0])
        user = User.objects.create_user(
            **validated_data,
            user_type=user_type
        )
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
        read_only_fields = ['created_at', 'updated_at', 'user', 'status']

    def validate(self, data):
        # Check if end date is after start date
        if 'end_date' in data and 'start_date' in data:
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })

        # Check property availability for the selected dates
        if 'property' in data and 'start_date' in data and 'end_date' in data:
            property = data['property']
            start_date = data['start_date']
            end_date = data['end_date']
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                property=property,
                status__in=['PENDING', 'CONFIRMED'],
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # If updating an existing booking, exclude it from the overlap check
            if self.instance:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
            
            if overlapping_bookings.exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['The property is already booked for the selected dates.']
                })
        
        return data
    
    def create(self, validated_data):
        # Set the current user as the booking user
        validated_data['user'] = self.context['request'].user
        
        # Set default status to PENDING for new bookings
        if 'status' not in validated_data:
            validated_data['status'] = 'PENDING'
            
        # Calculate total price if not provided
        if 'total_price' not in validated_data and 'property' in validated_data:
            days = (validated_data['end_date'] - validated_data['start_date']).days + 1
            validated_data['total_price'] = days * validated_data['property'].price
            
        return super().create(validated_data)


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
