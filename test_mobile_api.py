#!/usr/bin/env python3
"""
Test script for Mobile App API endpoints
Tests QR scanning, trip start/stop, and passenger tracking
"""

import requests
import json
import time

# API Base URL (adjust if needed)
BASE_URL = "http://localhost:8000/api"

def test_qr_scan():
    """Test QR code scanning endpoint"""
    print("\n🔍 Testing QR Code Scanning...")
    
    # Use a real QR code from Firebase
    qr_code = "terminal_id:PjYqQNctdioMF2OvrbiN"  # Dipolog Terminal
    
    response = requests.post(f"{BASE_URL}/scan-qr/", 
                           json={"qr_code": qr_code},
                           headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ QR Code scanning works!")
            return data['terminal']['terminal_id']
        else:
            print("❌ QR Code scanning failed!")
            return None
    else:
        print("❌ QR Code scanning request failed!")
        return None

def test_start_trip(terminal_id):
    """Test trip start endpoint"""
    print("\n🚀 Testing Trip Start...")
    
    # Use real driver ID from Firebase
    trip_data = {
        "driver_id": "vWCHpexWfZNTj6Jf85D5",  # Real driver from Firebase
        "start_terminal": terminal_id,
        "destination_terminal": "cu38ZbDlEWIiglCD5P54",  # Molave Terminal
        "passengers": 15
    }
    
    response = requests.post(f"{BASE_URL}/trips/start/", 
                           json=trip_data,
                           headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Trip start works!")
            return data['trip_id']
        else:
            print("❌ Trip start failed!")
            return None
    else:
        print("❌ Trip start request failed!")
        return None

def test_update_passengers(trip_id):
    """Test passenger count update endpoint"""
    print("\n👥 Testing Passenger Count Update...")
    
    new_passenger_count = 20
    
    response = requests.post(f"{BASE_URL}/trips/{trip_id}/passengers/", 
                           json={"passengers": new_passenger_count},
                           headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Passenger count update works!")
            return True
        else:
            print("❌ Passenger count update failed!")
            return False
    else:
        print("❌ Passenger count update request failed!")
        return False

def test_get_active_trips():
    """Test get active trips endpoint"""
    print("\n📋 Testing Get Active Trips...")
    
    response = requests.get(f"{BASE_URL}/trips/active/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ Get active trips works! Found {data['count']} active trips")
            return True
        else:
            print("❌ Get active trips failed!")
            return False
    else:
        print("❌ Get active trips request failed!")
        return False

def test_stop_trip(trip_id):
    """Test trip stop endpoint"""
    print("\n🛑 Testing Trip Stop...")
    
    response = requests.post(f"{BASE_URL}/trips/{trip_id}/stop/", 
                           json={"passengers": 18},  # Final passenger count
                           headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Trip stop works!")
            return True
        else:
            print("❌ Trip stop failed!")
            return False
    else:
        print("❌ Trip stop request failed!")
        return False

def test_get_trip_details(trip_id):
    """Test get trip details endpoint"""
    print("\n📄 Testing Get Trip Details...")
    
    response = requests.get(f"{BASE_URL}/trips/{trip_id}/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Get trip details works!")
            return True
        else:
            print("❌ Get trip details failed!")
            return False
    else:
        print("❌ Get trip details request failed!")
        return False

def main():
    """Run all API tests"""
    print("🧪 Mobile App API Testing")
    print("=" * 50)
    
    try:
        # Test 1: QR Code Scanning
        terminal_id = test_qr_scan()
        if not terminal_id:
            print("❌ Cannot continue without valid terminal ID")
            return
        
        # Test 2: Start Trip
        trip_id = test_start_trip(terminal_id)
        if not trip_id:
            print("❌ Cannot continue without valid trip ID")
            return
        
        # Test 3: Update Passengers
        test_update_passengers(trip_id)
        
        # Test 4: Get Active Trips
        test_get_active_trips()
        
        # Test 5: Get Trip Details
        test_get_trip_details(trip_id)
        
        # Test 6: Stop Trip
        test_stop_trip(trip_id)
        
        print("\n" + "=" * 50)
        print("🎉 API Testing Complete!")
        print("Check your Django dashboard to see the new trip data.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
