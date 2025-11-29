"""
Test script for Driver CRUD operations with Firebase Firestore
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from monitoring.firebase_service import firebase_service
from datetime import datetime

def test_create_driver():
    """Test creating a driver"""
    print("\n=== Testing CREATE Driver ===")
    try:
        driver_data = {
            'name': 'Test Driver',
            'contact': '+63 912 345 6789',
            'license_number': 'N01-12-345678',
            'is_active': True,
        }
        driver_id = firebase_service.create_driver(driver_data)
        print(f"[OK] Driver created successfully with ID: {driver_id}")
        return driver_id
    except Exception as e:
        print(f"[FAIL] Error creating driver: {e}")
        return None

def test_read_driver(driver_id):
    """Test reading a driver"""
    print("\n=== Testing READ Driver ===")
    try:
        driver = firebase_service.get_driver(driver_id)
        if driver:
            print(f"[OK] Driver retrieved successfully:")
            for key, value in driver.items():
                print(f"  - {key}: {value}")
            return driver
        else:
            print(f"[FAIL] Driver not found")
            return None
    except Exception as e:
        print(f"[FAIL] Error reading driver: {e}")
        return None

def test_update_driver(driver_id):
    """Test updating a driver"""
    print("\n=== Testing UPDATE Driver ===")
    try:
        update_data = {
            'name': 'Updated Test Driver',
            'contact': '+63 987 654 3210',
            'license_number': 'N02-34-567890',
            'is_active': True,
        }
        success = firebase_service.update_driver(driver_id, update_data)
        if success:
            print(f"[OK] Driver updated successfully")
            # Verify update
            driver = firebase_service.get_driver(driver_id)
            print(f"  Updated name: {driver.get('name')}")
            print(f"  Updated contact: {driver.get('contact')}")
            return True
        else:
            print(f"[FAIL] Failed to update driver")
            return False
    except Exception as e:
        print(f"[FAIL] Error updating driver: {e}")
        return False

def test_list_drivers():
    """Test listing all drivers"""
    print("\n=== Testing LIST All Drivers ===")
    try:
        drivers = firebase_service.get_all_drivers()
        print(f"[OK] Retrieved {len(drivers)} driver(s):")
        for driver in drivers:
            print(f"  - {driver.get('name')} (ID: {driver.get('driver_id', driver.get('id'))[:8]})")
        return drivers
    except Exception as e:
        print(f"[FAIL] Error listing drivers: {e}")
        return []

def test_delete_driver(driver_id):
    """Test deleting a driver"""
    print("\n=== Testing DELETE Driver ===")
    try:
        success = firebase_service.delete_driver(driver_id)
        if success:
            print(f"[OK] Driver deleted successfully")
            # Verify deletion
            driver = firebase_service.get_driver(driver_id)
            if driver is None:
                print(f"  Confirmed: Driver no longer exists")
            return True
        else:
            print(f"[FAIL] Failed to delete driver")
            return False
    except Exception as e:
        print(f"[FAIL] Error deleting driver: {e}")
        return False

def run_all_tests():
    """Run all CRUD tests"""
    print("\n" + "="*60)
    print("Driver CRUD Operations Test Suite")
    print("="*60)
    
    # Test CREATE
    driver_id = test_create_driver()
    if not driver_id:
        print("\n[ERROR] Cannot continue tests without creating a driver")
        return
    
    # Test READ
    driver = test_read_driver(driver_id)
    if not driver:
        print("\n[ERROR] Cannot continue tests without reading the driver")
        return
    
    # Test UPDATE
    test_update_driver(driver_id)
    
    # Test LIST
    test_list_drivers()
    
    # Test DELETE
    test_delete_driver(driver_id)
    
    # Verify deletion
    verify = test_read_driver(driver_id)
    if verify is None:
        print("\n[SUCCESS] All CRUD operations completed successfully!")
    else:
        print("\n[ERROR] Driver was not properly deleted")

if __name__ == '__main__':
    run_all_tests()
