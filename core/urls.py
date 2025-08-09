from django.urls import path
from .views import (
    UserRegistrationView,
    UserListView,
    UserDetailView,
    PropertyListView,
    PropertyCreateView,
    PropertyDetailView,
    PropertyUpdateView,
    PropertyDeleteView,
    SubscriptionListView,
    SubscriptionDetailView,
    TransactionListView,
    TransactionDetailView
)

urlpatterns = [
    # Users
    path('users/register/', UserRegistrationView.as_view(), name='user-register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Properties
    path('properties/', PropertyListView.as_view(), name='property-list'),
    path('properties/create/', PropertyCreateView.as_view(), name='property-create'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('properties/<int:pk>/update/', PropertyUpdateView.as_view(), name='property-update'),
    path('properties/<int:pk>/delete/', PropertyDeleteView.as_view(), name='property-delete'),
    
    # Subscriptions
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    
    # Transactions
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
]




# from django.urls import path
# from .views import (
#     UserRegistrationView,
#     UserListView,
#     UserDetailView,
#     PropertyListView,
#     PropertyCreateView,
#     PropertyDetailView,
#     PropertyUpdateView,
#     PropertyDeleteView,
#     SubscriptionListView,
#     SubscriptionDetailView,
#     TransactionListView,
#     TransactionDetailView
# )

# urlpatterns = [
#     # User endpoints
#     path('users/register/', UserRegistrationView.as_view(), name='user-register'),
#     path('users/', UserListView.as_view(), name='user-list'),
#     path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
#     # Property endpoints
#     path('properties/', PropertyListView.as_view(), name='property-list'),
#     path('properties/create/', PropertyCreateView.as_view(), name='property-create'),
#     path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
#     path('properties/<int:pk>/update/', PropertyUpdateView.as_view(), name='property-update'),
#     path('properties/<int:pk>/delete/', PropertyDeleteView.as_view(), name='property-delete'),
    
#     # Subscription endpoints
#     path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
#     path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    
#     # Transaction endpoints
#     path('transactions/', TransactionListView.as_view(), name='transaction-list'),
#     path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
# ]