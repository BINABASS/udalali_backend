from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, DurationField
from datetime import datetime, timedelta
from .models import User, Property, PropertyImage, Booking, Message, Report
from .serializers import (
    PropertySerializer, PropertyImageSerializer,
    BookingSerializer, MessageSerializer, ReportSerializer, UserSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsSellerUser, IsOwnerOrReadOnly, IsOwner
from django.db.models.functions import Coalesce

class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing properties with enhanced seller and buyer functionality.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, filters.DjangoFilterBackend]
    search_fields = ['title', 'description', 'location', 'property_type', 'amenities__name']
    ordering_fields = ['price', 'created_at', 'updated_at', 'average_rating']
    ordering = ['-created_at']
    filterset_fields = {
        'property_type': ['exact', 'in'],
        'price': ['gte', 'lte', 'exact'],
        'bedrooms': ['gte', 'lte', 'exact'],
        'bathrooms': ['gte', 'lte', 'exact'],
        'is_available': ['exact'],
        'seller': ['exact'],
        'created_at': ['date__gte', 'date__lte', 'date__range'],
    }

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'my_properties']:
            permission_classes = [IsAuthenticated, IsSellerUser]
        elif self.action in ['update', 'partial_update', 'destroy', 'upload_images']:
            permission_classes = [IsAuthenticated, IsOwner | IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally restricts the returned properties based on query parameters.
        """
        queryset = Property.objects.annotate(
            average_rating=Coalesce(Avg('reviews__rating'), 0.0),
            review_count=Count('reviews')
        ).select_related('seller').prefetch_related('images', 'amenities')
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller_id')
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
            
        # Filter by availability
        if not self.request.user.is_staff and self.action != 'retrieve':
            queryset = queryset.filter(is_available=True)
            
        # Filter by date availability
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Find properties that don't have conflicting bookings
                available_properties = Property.objects.filter(
                    ~Q(bookings__status__in=['CONFIRMED', 'PENDING']) |
                    ~Q(bookings__start_date__lte=end, bookings__end_date__gte=start)
                )
                queryset = queryset.filter(id__in=available_properties)
            except ValueError:
                pass
                
        return queryset.distinct()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsSellerUser])
    def my_properties(self, request):
        """
        Get properties listed by the current user (seller)
        """
        queryset = self.filter_queryset(
            self.get_queryset().filter(seller=request.user)
        )
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwner])
    def upload_images(self, request, pk=None):
        """
        Upload multiple images for a property
        """
        property = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'detail': 'No images provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        created_images = []
        for image in images:
            img = PropertyImage.objects.create(
                property=property,
                image=image,
                caption=request.data.get('caption', '')
            )
            created_images.append({
                'id': img.id,
                'image': request.build_absolute_uri(img.image.url),
                'caption': img.caption,
                'is_primary': img.is_primary
            })
            
        return Response(created_images, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
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
                'message': 'Both start_date and end_date are required',
                'next_available_dates': self._get_next_available_dates(property)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start >= end:
                return Response({
                    'available': False,
                    'message': 'End date must be after start date',
                    'next_available_dates': self._get_next_available_dates(property)
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Check for conflicting bookings
            is_available = not property.bookings.filter(
                status__in=['CONFIRMED', 'PENDING'],
                start_date__lte=end,
                end_date__gte=start
            ).exists()
            
            return Response({
                'available': is_available,
                'message': 'Property is available for the selected dates' if is_available 
                          else 'Property is not available for the selected dates',
                'next_available_dates': self._get_next_available_dates(property, start) if not is_available else None
            })
            
        except ValueError as e:
            return Response({
                'available': False,
                'message': 'Invalid date format. Please use YYYY-MM-DD format',
                'next_available_dates': self._get_next_available_dates(property)
            }, status=status.HTTP_400_BAD_REQUEST)

    def _get_next_available_dates(self, property, from_date=None):
        """
        Helper method to get the next available dates for a property
        """
        from_date = from_date or timezone.now().date()
        
        # Get all booked date ranges in the next 6 months
        booked_ranges = property.bookings.filter(
            status__in=['CONFIRMED', 'PENDING'],
            end_date__gte=from_date,
            start_date__lte=from_date + timedelta(days=180)  # Look ahead 6 months
        ).values_list('start_date', 'end_date')
        
        # Find the first available date range
        current_date = from_date
        for start, end in sorted(booked_ranges):
            if current_date < start:
                return {
                    'start_date': current_date.isoformat(),
                    'end_date': (start - timedelta(days=1)).isoformat()
                }
            current_date = max(current_date, end + timedelta(days=1))
            
        # If we get here, all dates after the last booking are available
        return {
            'start_date': current_date.isoformat(),
            'end_date': (current_date + timedelta(days=30)).isoformat()  # Default to 30 days
        }

    def perform_create(self, serializer):
        """
        Set the seller to the current user when creating a property
        """
        if not hasattr(self.request.user, 'user_type') or self.request.user.user_type != 'SELLER':
            raise serializers.ValidationError("Only sellers can create properties")
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure only the seller can update their own properties
        """
        if self.get_object().seller != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to update this property")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Ensure only the seller or admin can delete properties
        """
        if instance.seller != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this property")
        instance.delete()

# Note: Other ViewSets (BookingViewSet, MessageViewSet, etc.) would be enhanced in a similar way
# but are omitted for brevity. Each would get similar treatment with proper permissions,
# filtering, and actions specific to their functionality.
