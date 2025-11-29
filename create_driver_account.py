#!/usr/bin/env python
"""
Script to create a driver account linked to the admin user.
Run this script using: python manage.py shell < create_driver_account.py
Or: python create_driver_account.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
django.setup()

from monitoring.firebase_service import firebase_service

def create_driver_account():
    """Create or update driver account for admin user"""
    email = 'admin@mobilefleet.local'
    driver_name = 'Admin Driver'
    contact = '+63-900-000-0000'
    license_number = 'DL-2025-00001'
    
    # Get all existing drivers
    drivers = firebase_service.get_all_drivers()
    
    # Check if driver with this email already exists
    existing_driver = None
    for driver in drivers:
        if driver.get('email') == email:
            existing_driver = driver
            break
    
    # Create driver data
    driver_data = {
        'name': driver_name,
        'email': email,
        'contact': contact,
        'license_number': license_number,
        'is_active': True,
    }
    
    if existing_driver:
        # Update existing driver
        driver_id = existing_driver.get('driver_id') or existing_driver.get('id')
        success = firebase_service.update_driver(driver_id, driver_data)
        
        if success:
            print(f"[OK] Driver account updated for {email}")
            print(f"     Driver ID: {driver_id}")
        else:
            print(f"[ERROR] Failed to update driver account")
    else:
        # Create new driver
        driver_id = firebase_service.create_driver(driver_data)
        
        if driver_id:
            print(f"[OK] Driver account created successfully")
            print(f"     Email: {email}")
            print(f"     Driver ID: {driver_id}")
            print(f"     Name: {driver_name}")
        else:
            print(f"[ERROR] Failed to create driver account")
            return
    
    print("\n" + "="*60)
    print("MOBILE APP LOGIN CREDENTIALS")
    print("="*60)
    print(f"Email:    {email}")
    print(f"Password: Admin123!")
    print("="*60)
    print("\nYou can now login to the mobile app with these credentials.")

if __name__ == '__main__':
    create_driver_account()
