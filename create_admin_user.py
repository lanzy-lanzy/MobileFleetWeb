#!/usr/bin/env python
"""
Script to create an admin user for the Mobile Fleet application.
Run this script using: python manage.py shell < create_admin_user.py
Or: python create_admin_user.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """Create or update admin user"""
    username = 'admin'
    email = 'admin@mobilefleet.local'
    password = 'Admin123!'
    
    # Check if user exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"[OK] Admin user '{username}' already exists. Password updated.")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        print(f"[OK] Admin user '{username}' created successfully.")
    
    print("\n" + "="*50)
    print("LOGIN CREDENTIALS")
    print("="*50)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("="*50)

if __name__ == '__main__':
    create_admin_user()
