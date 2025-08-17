from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView
from core.authentication import CustomTokenObtainPairView

# Swagger/OpenAPI configuration
schema_view = get_schema_view(
    openapi.Info(
        title="DigiDalali API",
        default_version='v1',
        description="Property Marketplace API with enhanced seller and buyer functionality",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@digidalali.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# API URL patterns
api_patterns = [
    # Core API endpoints (using our enhanced configuration)
    path('', include('core.urls_enhanced')),  # Using the enhanced URLs
    
    # Users app endpoints
    path('users/', include('users.urls')),
    
    # Authentication endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints (versioned)
    path('api/v1/', include(api_patterns)),
    
    # REST Framework session-based authentication (for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # API documentation endpoints
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Redirect root to API documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
]

# Serve media & static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
