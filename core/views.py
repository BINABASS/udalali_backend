from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
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
        # Users can only see their own bookings unless they are staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

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
