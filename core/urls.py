from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Property URLs
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

# Booking URLs
router.register(r'bookings', views.BookingViewSet, basename='booking')
# This creates the following URLs:
# GET /bookings/ - List all bookings (user's bookings for regular users, all for staff)
# POST /bookings/ - Create a new booking
# GET /bookings/{id}/ - Get booking details
# PUT /bookings/{id}/ - Update booking
# DELETE /bookings/{id}/ - Cancel booking
# POST /bookings/{id}/cancel/ - Cancel a booking

# Message URLs
router.register(r'messages', views.MessageViewSet, basename='message')
# This creates the following URLs:
# GET /messages/ - List all messages (user's messages for regular users, all for staff)
# POST /messages/ - Send a new message
# GET /messages/{id}/ - Get message details
# PUT /messages/{id}/ - Update message
# DELETE /messages/{id}/ - Delete message
# POST /messages/{id}/mark_read/ - Mark message as read
# GET /messages/unread_count/ - Get count of unread messages

# Report URLs
router.register(r'reports', views.ReportViewSet, basename='report')
# This creates the following URLs:
# GET /reports/ - List all reports (user's reports for regular users, all for staff)
# POST /reports/ - Create a new report
# GET /reports/{id}/ - Get report details
# PUT /reports/{id}/ - Update report
# POST /reports/{id}/resolve/ - Resolve a report (admin only)

urlpatterns = [
    path('', include(router.urls)),
    path('properties/<int:property_pk>/', include(property_router.urls)),
    # Add other URL patterns as needed
]