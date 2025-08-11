import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

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

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['property']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"Booking {self.id} - {self.property.title} by {self.user.username}"


class Message(models.Model):
    MESSAGE_TYPES = (
        ('INQUIRY', 'Inquiry'),
        ('RESPONSE', 'Response'),
        ('GENERAL', 'General'),
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='GENERAL'
    )
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['recipient']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_message_type_display()} from {self.sender.username} to {self.recipient.username}"


class Report(models.Model):
    REPORT_TYPES = (
        ('PROPERTY', 'Property Report'),
        ('USER', 'User Report'),
        ('SYSTEM', 'System Report'),
        ('FINANCIAL', 'Financial Report'),
    )

    REPORT_STATUS = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    )

    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        default='PROPERTY'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports_submitted'
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_against'
    )
    reported_property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS,
        default='PENDING'
    )
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_resolved'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['reported_by']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title} ({self.get_status_display()})"
