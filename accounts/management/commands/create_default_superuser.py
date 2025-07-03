from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create default superuser for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user exists (will update existing user)',
        )

    def handle(self, *args, **options):
        email = 'amazingjimmy44@gmail.com'
        password = 'Amazing44.'
        first_name = 'Jimmy'
        last_name = 'Admin'

        try:
            if User.objects.filter(email=email).exists():
                if options['force']:
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Superuser updated successfully!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  Superuser with email {email} already exists.')
                    )
                    self.stdout.write(
                        self.style.WARNING('   Use --force to update existing user.')
                    )
            else:
                User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser created successfully!')
                )
            
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Name: {first_name} {last_name}')
            self.stdout.write(f'   Password: [Hidden for security]')
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {e}')
            )
