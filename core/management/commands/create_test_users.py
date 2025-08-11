from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test users with different roles for development and testing'

    def handle(self, *args, **options):
        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@udalali.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
                'phone': '+255700000001',
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            self.stdout.write('Admin user already exists')

        # Seller user
        seller, created = User.objects.get_or_create(
            username='seller',
            defaults={
                'email': 'seller@udalali.com',
                'first_name': 'John',
                'last_name': 'Seller',
                'user_type': 'SELLER',
                'is_verified': True,
                'phone': '+255700000002',
            }
        )
        if created:
            seller.set_password('seller123')
            seller.save()
            self.stdout.write(self.style.SUCCESS('Successfully created seller user'))
        else:
            self.stdout.write('Seller user already exists')

        # Buyer user
        buyer, created = User.objects.get_or_create(
            username='buyer',
            defaults={
                'email': 'buyer@udalali.com',
                'first_name': 'Jane',
                'last_name': 'Buyer',
                'user_type': 'CUSTOMER',
                'is_verified': True,
                'phone': '+255700000003',
            }
        )
        if created:
            buyer.set_password('buyer123')
            buyer.save()
            self.stdout.write(self.style.SUCCESS('Successfully created buyer user'))
        else:
            self.stdout.write('Buyer user already exists')

        self.stdout.write(self.style.SUCCESS('\nTest users created successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write(self.style.SUCCESS('\nAdmin:'))
        self.stdout.write('Username: admin')
        self.stdout.write('Password: admin123')
        self.stdout.write(self.style.SUCCESS('\nSeller:'))
        self.stdout.write('Username: seller')
        self.stdout.write('Password: seller123')
        self.stdout.write(self.style.SUCCESS('\nBuyer:'))
        self.stdout.write('Username: buyer')
        self.stdout.write('Password: buyer123')
