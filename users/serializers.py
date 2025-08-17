from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='A user with this email already exists.'
            )
        ],
        help_text='Required. Must be a valid email address.'
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text='Your password must be at least 8 characters long and not too common.'
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Enter the same password as above, for verification.'
    )
    role = serializers.ChoiceField(
        choices=[('CUSTOMER', 'Customer'), ('SELLER', 'Seller')],
        required=True,
        help_text='Select your role: Customer or Seller.'
    )
    phone_number = serializers.CharField(
        required=True,
        max_length=20,
        help_text='Your primary contact number (e.g., +255 712 345 678).',
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='This phone number is already in use.'
            )
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'role', 'phone_number')
        extra_kwargs = {
            'username': {
                'required': True,
                'help_text': 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message='A user with that username already exists.'
                    )
                ]
            },
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        
        # Validate phone number format (basic validation)
        phone_number = attrs.get('phone_number', '').strip()
        if not phone_number:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
            
        # Simple phone number validation (can be enhanced with a library like phonenumbers)
        if not re.match(r'^\+?[\d\s-]{10,20}$', phone_number):
            raise serializers.ValidationError({
                "phone_number": "Enter a valid phone number (e.g., +255 712 345 678)."
            })
            
        return attrs

    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password')
        
        # Extract role and phone_number
        role = validated_data.pop('role')
        phone_number = validated_data.pop('phone_number')
        
        # Create user with all fields
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=phone_number,
            user_type=role
        )
        
        return user
