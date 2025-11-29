#!/usr/bin/env python
"""
Fix existing drivers that don't have Django user accounts.
This script creates Django users for drivers already in Firebase.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
django.setup()

from django.contrib.auth.models import User
from monitoring.firebase_service import firebase_service

def fix_existing_drivers():
    """Create Django users for existing drivers"""
    
    print("="*70)
    print("FIXING EXISTING DRIVERS - Creating Django User Accounts")
    print("="*70)
    print()
    
    # Get all drivers from Firebase
    drivers = firebase_service.get_all_drivers()
    
    if not drivers:
        print("No drivers found in Firebase.")
        return
    
    print(f"Found {len(drivers)} driver(s) in Firebase\n")
    
    fixed_count = 0
    already_have_count = 0
    error_count = 0
    
    for driver in drivers:
        driver_id = driver.get('driver_id') or driver.get('id')
        email = driver.get('email')
        name = driver.get('name', 'Unknown')
        django_user_id = driver.get('django_user_id')
        
        print(f"Processing: {name} ({email})")
        
        # Check if driver already has Django user
        if django_user_id:
            print(f"  ✓ Already has Django user (ID: {django_user_id})")
            already_have_count += 1
            print()
            continue
        
        # Check if Django user exists with this email
        user = User.objects.filter(email=email).first()
        
        if user:
            print(f"  ! Django user already exists but not linked")
            # Update driver with Django user ID
            firebase_service.update_driver(
                driver_id,
                {'django_user_id': user.id}
            )
            print(f"  ✓ Linked to Django user (ID: {user.id})")
            fixed_count += 1
        else:
            print(f"  → Creating new Django user...")
            try:
                # Create Django user
                name_parts = name.split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='TempPassword123!',  # Temporary password
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Update driver with Django user ID
                firebase_service.update_driver(
                    driver_id,
                    {'django_user_id': user.id}
                )
                
                print(f"  ✓ Created Django user successfully")
                print(f"    User ID: {user.id}")
                print(f"    Temporary Password: TempPassword123!")
                print(f"    ⚠️  Driver should change password on first login!")
                fixed_count += 1
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                error_count += 1
        
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total drivers processed: {len(drivers)}")
    print(f"Already had Django users: {already_have_count}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    print()
    
    if fixed_count > 0:
        print("SUCCESS! Drivers can now login to mobile app.")
        print()
        print("Next steps:")
        print("1. Share driver email and temporary password with them")
        print("2. Ask them to change password on first login")
        print("3. They can now use the mobile app")
    
    if error_count > 0:
        print(f"\nWarning: {error_count} driver(s) failed to fix.")
        print("Please check the error messages above.")
    
    print()

if __name__ == '__main__':
    fix_existing_drivers()
