from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPES = (
        ('ADMIN', 'Admin'),
        ('SELLER', 'Seller'),
        ('BUYER', 'Buyer'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='BUYER')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Fix for reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='core_user_groups',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='core_user_permissions',
        related_query_name='core_user',
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Property(models.Model):
    PROPERTY_TYPES = (
        ('HOUSE', 'House'),
        ('VEHICLE', 'Vehicle'),
    )
    
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='properties'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    property_type = models.CharField(
        max_length=10, 
        choices=PROPERTY_TYPES,
        default='HOUSE'
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_property_type_display()}"

class Subscription(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.seller.username}'s {self.plan_name} Subscription"

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"Transaction #{self.id} - {self.property.title}"