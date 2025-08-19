#!/usr/bin/env python
"""
Firebase Connection Test Script
This script tests the Firebase Firestore connection and basic CRUD operations.
"""

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
django.setup()

from monitoring.firebase_service import firebase_service

def test_firebase_connection():
    """Test Firebase connection and basic operations"""
    print("🔥 Testing Firebase Connection...")
    print("=" * 50)

    try:
        # Test 1: Check if Firebase service initializes
        print("1. Testing Firebase initialization...")
        if firebase_service.db is None:
            print("❌ Firebase initialization failed!")
            return False
        print("✅ Firebase initialized successfully!")

        # Test 2: Test terminal creation
        print("\n2. Testing terminal creation...")
        test_terminal = {
            'name': 'Test Terminal - Dumingag',
            'latitude': 8.1234,
            'longitude': 123.5678,
            'is_active': True,
        }

        terminal_id = firebase_service.create_terminal(test_terminal)
        if terminal_id:
            print(f"✅ Terminal created successfully! ID: {terminal_id}")
        else:
            print("❌ Failed to create terminal!")
            return False

        # Test 3: Test terminal retrieval
        print("\n3. Testing terminal retrieval...")
        retrieved_terminal = firebase_service.get_terminal(terminal_id)
        if retrieved_terminal:
            print(f"✅ Terminal retrieved successfully!")
            print(f"   Name: {retrieved_terminal.get('name')}")
            print(f"   Location: {retrieved_terminal.get('latitude')}, {retrieved_terminal.get('longitude')}")
        else:
            print("❌ Failed to retrieve terminal!")
            return False

        # Test 4: Test driver creation
        print("\n4. Testing driver creation...")
        test_driver = {
            'name': 'Juan Dela Cruz',
            'contact': '+63 912 345 6789',
            'license_number': 'N01-12-345678',
            'is_active': True,
        }

        driver_id = firebase_service.create_driver(test_driver)
        if driver_id:
            print(f"✅ Driver created successfully! ID: {driver_id}")
        else:
            print("❌ Failed to create driver!")
            return False

        # Test 5: Test trip creation
        print("\n5. Testing trip creation...")
        test_trip = {
            'driver_id': driver_id,
            'start_terminal': terminal_id,
            'destination_terminal': terminal_id,  # Same terminal for test
            'passengers': 15,
            'status': 'in_progress',
        }

        trip_id = firebase_service.create_trip(test_trip)
        if trip_id:
            print(f"✅ Trip created successfully! ID: {trip_id}")
        else:
            print("❌ Failed to create trip!")
            return False

        # Test 6: Test data listing
        print("\n6. Testing data retrieval...")
        terminals = firebase_service.get_all_terminals()
        drivers = firebase_service.get_all_drivers()
        trips = firebase_service.get_all_trips()

        print(f"✅ Found {len(terminals)} terminals")
        print(f"✅ Found {len(drivers)} drivers")
        print(f"✅ Found {len(trips)} trips")

        # Test 7: Test trip status update
        print("\n7. Testing trip status update...")
        update_success = firebase_service.update_trip(trip_id, {
            'status': 'completed',
            'arrival_time': datetime.now()
        })

        if update_success:
            print("✅ Trip status updated successfully!")
        else:
            print("❌ Failed to update trip status!")
            return False

        # Test 8: Clean up test data
        print("\n8. Cleaning up test data...")
        cleanup_success = True

        if not firebase_service.delete_trip(trip_id):
            print("⚠️  Failed to delete test trip")
            cleanup_success = False

        if not firebase_service.delete_driver(driver_id):
            print("⚠️  Failed to delete test driver")
            cleanup_success = False

        if not firebase_service.delete_terminal(terminal_id):
            print("⚠️  Failed to delete test terminal")
            cleanup_success = False

        if cleanup_success:
            print("✅ Test data cleaned up successfully!")

        print("\n" + "=" * 50)
        print("🎉 All Firebase tests passed successfully!")
        print("🔥 Firebase integration is working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ Firebase test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_firebase_connection()
    if success:
        print("\n✅ Firebase is ready for production use!")
        print("\n📋 Next steps:")
        print("   1. Add your Cloudinary credentials to .env file")
        print("   2. Start the Django server: python manage.py runserver")
        print("   3. Access the dashboard at http://localhost:8000/")
    else:
        print("\n❌ Firebase setup needs attention!")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file configuration")
        print("   2. Verify mobile_fleet_services.json file exists")
        print("   3. Ensure Firebase project has Firestore enabled")

    sys.exit(0 if success else 1)