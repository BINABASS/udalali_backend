from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User, Property, Subscription, Transaction

USER_TYPE_CHOICES = [
    ('seller', 'Seller'),
    ('buyer', 'Buyer'),
]

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'user_type')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ('username', 'email', 'phone', 'user_type', 'is_verified', 'is_staff')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'phone', 'user_type')}),
        (_('Permissions'), {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser',
                      'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'user_type', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions',)

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'property_type', 'formatted_price', 'location', 
                   'is_available', 'created_at')
    list_filter = ('property_type', 'is_available')
    search_fields = ('title', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('seller',)
    
    def formatted_price(self, obj):
        return f"${obj.price:,.2f}"
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('seller', 'plan_name', 'formatted_price', 'start_date', 'end_date', 'active_status')
    list_filter = ('start_date', 'end_date')
    search_fields = ('seller__username', 'plan_name')
    raw_id_fields = ('seller',)
    
    def formatted_price(self, obj):
        return f"${obj.price:,.2f}"
    formatted_price.short_description = 'Price'
    
    def active_status(self, obj):
        return obj.is_active
    active_status.boolean = True
    active_status.short_description = 'Is Active'

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'buyer', 'formatted_amount', 'status', 'transaction_date_short')
    list_filter = ('status',)
    search_fields = ('property__title', 'buyer__username')
    raw_id_fields = ('buyer', 'property')
    readonly_fields = ('transaction_date',)
    
    def formatted_amount(self, obj):
        return f"${obj.amount:,.2f}"
    formatted_amount.short_description = 'Amount'
    
    def transaction_date_short(self, obj):
        return obj.transaction_date.strftime("%Y-%m-%d %H:%M")
    transaction_date_short.short_description = 'Transaction Date'

# Admin site configuration
admin.site.register(User, CustomUserAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Transaction, TransactionAdmin)

admin.site.site_header = 'DigiDalali Administration'
admin.site.site_title = 'DigiDalali Admin Portal'
admin.site.index_title = 'Welcome to DigiDalali Admin'

from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls')),
]