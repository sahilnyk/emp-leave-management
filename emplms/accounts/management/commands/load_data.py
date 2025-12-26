from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from faker import Faker

class Command(BaseCommand):
    help = 'Load 50 employees and 1 manager'

    def handle(self, *args, **kwargs):
        fake = Faker('en_IN')
        
        User.objects.all().delete()
        
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='Test@123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        Profile.objects.update_or_create(user=manager_user, defaults={'role': 'manager'})
        self.stdout.write(self.style.SUCCESS(f'Created manager: {manager_user.username}'))
        
        for i in range(1, 51):
            username = f'employee{i}'
            emp_user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='Test@123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            Profile.objects.update_or_create(user=emp_user, defaults={'role': 'employee'})
            self.stdout.write(self.style.SUCCESS(f'Created {username}: {emp_user.first_name} {emp_user.last_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal: {User.objects.count()} users (1 manager + 50 employees)'))