from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet, basename='property')
# This creates the following URLs:
# GET /properties/ - List all properties
# POST /properties/ - Create new property
# GET /properties/{id}/ - Get property details
# PUT /properties/{id}/ - Update property
# DELETE /properties/{id}/ - Delete property
# POST /properties/{id}/set_primary_image/ - Set primary image

# Nested router for property images
property_router = DefaultRouter()
property_router.register(r'images', views.PropertyImageViewSet, basename='property-image')

urlpatterns = [
    path('', include(router.urls)),
    path('properties/<int:property_pk>/', include(property_router.urls)),
    # Add other URL patterns as needed
]
