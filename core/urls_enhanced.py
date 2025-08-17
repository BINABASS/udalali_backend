from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_nested import routers
from . import views
from .views_enhanced import PropertyViewSet
from .views import current_user, BookingViewSet, MessageViewSet, ReportViewSet, PropertyImageViewSet

# Main API router
router = DefaultRouter()

# Property URLs with enhanced functionality
router.register(r'properties', PropertyViewSet, basename='property')
# This creates the following URLs:
# GET /properties/ - List all available properties (filterable)
# POST /properties/ - Create new property (seller only)
# GET /properties/{id}/ - Get property details
# PUT /properties/{id}/ - Update property (owner or admin only)
# DELETE /properties/{id}/ - Delete property (owner or admin only)
# GET /properties/my_properties/ - Get current user's properties (seller only)
# POST /properties/{id}/upload_images/ - Upload images for a property (owner or admin only)
# GET /properties/{id}/availability/ - Check property availability for given dates

# Nested router for property images
property_router = routers.NestedSimpleRouter(router, r'properties', lookup='property')
property_router.register(r'images', PropertyImageViewSet, basename='property-image')
# This creates the following nested URLs:
# GET /properties/{property_pk}/images/ - List all images for a property
# POST /properties/{property_pk}/images/ - Add an image to a property
# GET /properties/{property_pk}/images/{id}/ - Get image details
# PUT /properties/{property_pk}/images/{id}/ - Update image (owner or admin only)
# DELETE /properties/{property_pk}/images/{id}/ - Delete image (owner or admin only)

# Booking URLs
router.register(r'bookings', BookingViewSet, basename='booking')
# This creates the following URLs:
# GET /bookings/ - List user's bookings
# POST /bookings/ - Create a new booking
# GET /bookings/{id}/ - Get booking details
# PUT /bookings/{id}/ - Update booking (owner or admin only)
# DELETE /bookings/{id}/ - Cancel booking (owner or admin only)
# POST /bookings/{id}/cancel/ - Cancel a booking (owner or admin only)
# POST /bookings/{id}/confirm/ - Confirm a booking (property owner or admin only)
# POST /bookings/{id}/reject/ - Reject a booking (property owner or admin only)
# GET /bookings/seller/ - Get all bookings for seller's properties

# Message URLs
router.register(r'messages', MessageViewSet, basename='message')
# This creates the following URLs:
# GET /messages/ - List user's messages
# POST /messages/ - Send a new message
# GET /messages/{id}/ - Get message details
# PUT /messages/{id}/ - Update message (sender only)
# DELETE /messages/{id}/ - Delete message (sender or recipient)
# POST /messages/{id}/mark_read/ - Mark message as read (recipient only)
# GET /messages/unread_count/ - Get count of unread messages

# Report URLs
router.register(r'reports', ReportViewSet, basename='report')
# This creates the following URLs:
# GET /reports/ - List reports (user's reports for regular users, all for staff)
# POST /reports/ - Create a new report
# GET /reports/{id}/ - Get report details
# PUT /reports/{id}/ - Update report (reporter or admin only)
# POST /reports/{id}/resolve/ - Resolve a report (admin only)

urlpatterns = [
    # Main API endpoints
    path('', include(router.urls)),
    
    # Nested property image endpoints
    path('', include(property_router.urls)),
    
    # User endpoints
    path('users/me/', current_user, name='current-user'),
]
