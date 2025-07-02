from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a sample user for testing purposes'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(email='sample@example.com').exists():
            User.objects.create_user(
                email='sample@example.com',
                first_name='Sample',
                last_name='User',
                password='SamplePassword123',
                phone_number='+1234567890'
            )
            self.stdout.write(self.style.SUCCESS('Sample user created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Sample user already exists.'))
