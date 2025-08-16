import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['user_type'] = user.user_type
        return token

    def validate(self, attrs):
        logger.info(f"Authentication attempt with data: {attrs}")
        
        username = attrs.get('username')
        password = attrs.get('password')
        
        # First try to authenticate with provided credentials
        from django.contrib.auth import authenticate, get_user_model
        User = get_user_model()
        
        # Try to get user by username or email
        try:
            if '@' in username:
                user = User.objects.get(email=username)
                username = user.username
            else:
                user = User.objects.get(username=username)
                
            # Now authenticate with the found username
            user = authenticate(username=username, password=password)
            
            if user is None:
                logger.error("Authentication failed: Invalid password")
                raise Exception("Invalid password")
                
            if not user.is_active:
                logger.error(f"Authentication failed: User {username} is not active")
                raise Exception("User account is not active")
                
            # Get the token data
            refresh = self.get_token(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type,
                    'is_verified': user.is_verified,
                }
            }
            
            logger.info(f"Authentication successful for user: {user.username}")
            return data
            
        except User.DoesNotExist:
            logger.error(f"No user found with username/email: {username}")
            raise Exception("No active account found with the given credentials")
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise Exception("Authentication failed. Please try again.")

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
