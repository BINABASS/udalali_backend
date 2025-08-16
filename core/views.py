from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from .models import User, Property, PropertyImage, Booking, Message, Report
from .serializers import (
    PropertySerializer, PropertyImageSerializer,
    BookingSerializer, MessageSerializer, ReportSerializer, UserSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_available=True)
        return queryset

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def availability(self, request, pk=None):
        """
        Check if a property is available for the given dates
        """
        property = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'available': False,
                'message': 'Both start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Check if dates are valid
            if start >= end:
                return Response({
                    'available': False,
                    'message': 'End date must be after start date'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if property is available
            if not property.is_available:
                return Response({
                    'available': False,
                    'message': 'Property is not available for booking'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for conflicting bookings
            conflicting_bookings = Booking.objects.filter(
                property=property,
                status__in=['CONFIRMED', 'PENDING'],
                start_date__lt=end,
                end_date__gt=start
            )
            
            if conflicting_bookings.exists():
                return Response({
                    'available': False,
                    'message': 'Property is not available for the selected dates'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'available': True,
                'message': 'Property is available for the selected dates'
            })
            
        except ValueError:
            return Response({
                'available': False,
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def set_primary_image(self, request, pk=None):
        property = self.get_object()
        image_id = request.data.get('image_id')
        if not image_id:
            return Response({'error': 'image_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image = property.images.get(id=image_id)
        except PropertyImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Set all images to not primary first
        property.images.all().update(is_primary=False)
        # Set the selected image as primary
        image.is_primary = True
        image.save()
        
        return Response({'status': 'primary image set'})

class PropertyImageViewSet(viewsets.ModelViewSet):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyImage.objects.filter(property_id=self.kwargs['property_pk'])

    def perform_create(self, serializer):
        property = get_object_or_404(Property, pk=self.kwargs['property_pk'])
        if property.seller != self.request.user:
            self.permission_denied(self.request)
        serializer.save(property=property)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['property__title', 'notes']
    ordering_fields = ['start_date', 'end_date', 'created_at']

    def get_queryset(self):
        queryset = Booking.objects.all()
        
        # Filter by property if provided
        property_id = self.request.query_params.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
            
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        # Users can see:
        # 1. Their own bookings
        # 2. Bookings for properties they own (if they are sellers)
        # 3. All bookings if staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(user=self.request.user) |
                Q(property__seller=self.request.user)
            )
            
        return queryset.select_related('property', 'user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'CANCELLED':
            return Response(
                {'error': 'Booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'CANCELLED'
        booking.save()
        return Response({'status': 'booking cancelled'})

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending booking (seller only)"""
        booking = self.get_object()
        
        # Check if user is the seller of this property
        if booking.property.seller != request.user:
            return Response(
                {'error': 'Only the property seller can confirm bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'PENDING':
            return Response(
                {'error': f'Cannot confirm booking with status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CONFIRMED'
        booking.save()
        
        return Response({
            'status': 'booking confirmed',
            'message': f'Booking {booking.id} has been confirmed successfully'
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending booking (seller only)"""
        booking = self.get_object()
        
        # Check if user is the seller of this property
        if booking.property.seller != request.user:
            return Response(
                {'error': 'Only the property seller can reject bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'PENDING':
            return Response(
                {'error': f'Cannot reject booking with status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CANCELLED'
        booking.save()
        
        return Response({
            'status': 'booking rejected',
            'message': f'Booking {booking.id} has been rejected'
        })

    @action(detail=False, methods=['get'])
    def seller_bookings(self, request):
        """Get all bookings for properties owned by the current seller"""
        if request.user.user_type != 'SELLER':
            return Response(
                {'error': 'Only sellers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(property__seller=request.user)
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        # Filter by property if provided
        property_id = request.query_params.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'content', 'sender__username', 'recipient__username']
    ordering_fields = ['is_read', 'created_at']

    def get_queryset(self):
        queryset = Message.objects.all()
        # Users can only see messages where they are the sender or recipient
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(sender=self.request.user) | Q(recipient=self.request.user)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient != request.user:
            return Response(
                {'error': 'Not authorized to mark this message as read'},
                status=status.HTTP_403_FORBIDDEN
            )
        message.is_read = True
        message.save()
        return Response({'status': 'message marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'reported_by__username']
    ordering_fields = ['status', 'created_at', 'resolved_at']

    def get_queryset(self):
        queryset = Report.objects.all()
        # Regular users can only see their own reports
        if not self.request.user.is_staff:
            queryset = queryset.filter(reported_by=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def resolve(self, request, pk=None):
        report = self.get_object()
        if report.status == 'RESOLVED':
            return Response(
                {'error': 'Report is already resolved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report.status = 'RESOLVED'
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save()
        return Response({'status': 'report resolved'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get the current authenticated user's data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
