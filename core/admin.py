from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage, Booking, Message, Report

User = get_user_model()

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'price', 'location', 'status', 'is_available', 'created_at']
    list_filter = ['property_type', 'status', 'is_available']
    search_fields = ['title', 'description', 'location']
    inlines = [PropertyImageInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'property', 'user', 'start_date', 'end_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['property__title', 'user__username', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'sender', 'recipient', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read']
    search_fields = ['subject', 'content', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['sender', 'recipient', 'property']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'report_type', 'status', 'reported_by', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['title', 'description', 'reported_by__username']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['reported_by', 'reported_user', 'reported_property', 'resolved_by']

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'property', 'is_primary', 'created_at']
    list_filter = ['is_primary']
    search_fields = ['property__title']
    readonly_fields = ['created_at', 'updated_at']

# Custom User Admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_staff']
    list_filter = ['user_type', 'is_verified', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
        ('Custom Fields', {'fields': ('user_type', 'is_verified')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

# Only register the User model if it's not already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
