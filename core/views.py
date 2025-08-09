# core/views.py
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, Subscription, Transaction
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PropertySerializer,
    PropertyCreateSerializer,
    PropertyUpdateSerializer,
    SubscriptionSerializer,
    TransactionSerializer
)

User = get_user_model()

# ====================== User Views ======================
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'phone']

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        return self.request.user

# ====================== Property Views ======================
class PropertyListView(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'property_type': ['exact'],
        'location': ['exact', 'icontains'],
        'price': ['gte', 'lte'],
        'is_available': ['exact']
    }
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        return Property.objects.filter(is_available=True)

class PropertyCreateView(generics.CreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.AllowAny]

class PropertyUpdateView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Property.objects.all()
        return Property.objects.filter(seller=self.request.user)

class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Property.objects.all()
        return Property.objects.filter(seller=self.request.user)

# ====================== Subscription Views ======================
class SubscriptionListView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan_name', 'is_active']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(seller=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.user_type != 'SELLER':
            return Response(
                {"detail": "Only sellers can create subscriptions"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(seller=self.request.user)

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(seller=self.request.user)

# ====================== Transaction Views ======================
class TransactionListView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'property__property_type']
    ordering_fields = ['transaction_date', 'amount']
    ordering = ['-transaction_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(buyer=self.request.user)

    def perform_create(self, serializer):
        property_obj = serializer.validated_data['property']
        
        if not property_obj.is_available:
            return Response(
                {"detail": "This property is not available for purchase"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if property_obj.seller == self.request.user:
            return Response(
                {"detail": "You cannot buy your own property"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction = serializer.save(
            buyer=self.request.user,
            amount=property_obj.price,
            status='PENDING'
        )
        
        property_obj.is_available = False
        property_obj.save()

class TransactionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(buyer=self.request.user)

    def perform_update(self, serializer):
        allowed_fields = {'payment_reference', 'status'}
        if set(serializer.validated_data.keys()) - allowed_fields:
            return Response(
                {"detail": "You can only update payment reference and status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()