import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('SELLER', 'Seller'),
        ('ADMIN', 'Admin'),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='CUSTOMER'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Property(models.Model):
    PROPERTY_TYPES = (
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('LAND', 'Land'),
        ('COMMERCIAL', 'Commercial'),
        ('VEHICLE', 'Vehicle'),
    )

    STATUS_CHOICES = (
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    )

    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='properties'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPES,
        default='HOUSE'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type']),
            models.Index(fields=['price']),
            models.Index(fields=['location']),
            models.Index(fields=['status']),
            models.Index(fields=['is_available']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_property_type_display()}"

    @property
    def formatted_price(self):
        return f"${self.price:,.2f}"

class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']
        indexes = [
            models.Index(fields=['property', 'is_primary']),
        ]

    def __str__(self):
        return f"Image for {self.property.title} (Primary: {self.is_primary})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            self.__class__.objects.filter(
                property=self.property,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    notify_on_updates = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-created_at']

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='purchases'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sales'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['buyer']),
            models.Index(fields=['seller']),
            models.Index(fields=['created_at']),
        ]
