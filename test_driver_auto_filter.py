#!/usr/bin/env python
"""
Test script to verify driver auto-filtering in trip monitoring
Run with: python manage.py shell < test_driver_auto_filter.py
"""

from django.contrib.auth.models import User
from monitoring.firebase_service import firebase_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("DRIVER AUTO-FILTER TEST")
print("="*60)

# Get all users
users = User.objects.all()
print(f"\n✅ Total Django Users: {len(users)}")
for user in users:
    print(f"   - {user.username} (ID: {user.id}, Email: {user.email})")

# Get all drivers from Firebase
try:
    drivers = firebase_service.get_all_drivers()
    print(f"\n✅ Total Firebase Drivers: {len(drivers)}")
    for driver in drivers:
        driver_id = driver.get('driver_id') or driver.get('id')
        email = driver.get('email')
        django_id = driver.get('django_user_id')
        name = driver.get('name')
        print(f"   - {name} (ID: {driver_id})")
        print(f"     Email: {email}")
        print(f"     Django User ID: {django_id}")
except Exception as e:
    print(f"\n❌ Error loading drivers from Firebase: {e}")
    drivers = []

# Test matching logic
print(f"\n🔍 MATCHING TEST:")
for user in users:
    print(f"\n   User: {user.username} (ID: {user.id}, Email: {user.email})")
    matched = False
    for driver in drivers:
        driver_id = driver.get('driver_id') or driver.get('id')
        driver_email = driver.get('email', '').lower()
        user_email = user.email.lower()
        django_id = driver.get('django_user_id')
        driver_name = driver.get('name')
        
        # Check both matching criteria
        matches_django_id = (django_id == user.id)
        matches_email = (driver_email == user_email)
        
        if matches_django_id or matches_email:
            print(f"     ✅ MATCHED to driver: {driver_name} (ID: {driver_id})")
            if matches_django_id:
                print(f"        - By django_user_id: {django_id} == {user.id}")
            if matches_email:
                print(f"        - By email: {driver_email} == {user_email}")
            matched = True
            break
    
    if not matched:
        print(f"     ❌ NO MATCH FOUND")

# Get trips and check driver_id field
print(f"\n📊 TRIP DATA TEST:")
try:
    trips = firebase_service.get_all_trips()
    print(f"   Total trips: {len(trips)}")
    
    # Check driver_id field
    trips_with_driver = [t for t in trips if t.get('driver_id')]
    trips_without_driver = [t for t in trips if not t.get('driver_id')]
    
    print(f"   - With driver_id: {len(trips_with_driver)}")
    print(f"   - Without driver_id: {len(trips_without_driver)}")
    
    # Show unique driver IDs
    unique_drivers = set(t.get('driver_id') for t in trips_with_driver)
    print(f"   - Unique driver IDs in trips: {', '.join(str(d) for d in unique_drivers)}")
    
    if trips:
        print(f"\n   Sample trip:")
        sample = trips[0]
        print(f"     - ID: {sample.get('id')}")
        print(f"     - Driver ID: {sample.get('driver_id')}")
        print(f"     - Status: {sample.get('status')}")
except Exception as e:
    print(f"   ❌ Error loading trips: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
