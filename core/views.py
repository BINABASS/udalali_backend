from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Property, PropertyImage
from .serializers import PropertySerializer, PropertyImageSerializer

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

# Add any other view classes you had before
