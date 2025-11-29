#!/usr/bin/env python
"""
Test script for mobile login API endpoint
"""

import requests
import json

BASE_URL = 'http://localhost:8000'
API_LOGIN_ENDPOINT = f'{BASE_URL}/api/login/'

def test_mobile_login():
    """Test the mobile login endpoint"""
    
    print("="*60)
    print("MOBILE LOGIN API TEST")
    print("="*60)
    print(f"\nTesting endpoint: {API_LOGIN_ENDPOINT}\n")
    
    # Test data
    credentials = {
        'email': 'admin@mobilefleet.local',
        'password': 'Admin123!'
    }
    
    print(f"Credentials being tested:")
    print(f"  Email: {credentials['email']}")
    print(f"  Password: {credentials['password']}")
    print()
    
    try:
        # Make the request
        print("Sending login request...")
        response = requests.post(
            API_LOGIN_ENDPOINT,
            json=credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response Status: {response.status_code}\n")
        
        # Parse response
        data = response.json()
        
        print("Response Data:")
        print(json.dumps(data, indent=2))
        
        # Check for success
        if response.status_code == 200:
            print("\n" + "="*60)
            print("SUCCESS! Mobile login is working correctly.")
            print("="*60)
            
            if 'driver' in data:
                driver = data['driver']
                print(f"\nDriver Information:")
                print(f"  ID:      {driver.get('driver_id', 'N/A')}")
                print(f"  Name:    {driver.get('name', 'N/A')}")
                print(f"  Email:   {driver.get('email', 'N/A')}")
                print(f"  Contact: {driver.get('contact', 'N/A')}")
                print(f"  License: {driver.get('license_number', 'N/A')}")
        else:
            print("\n" + "="*60)
            print("LOGIN FAILED")
            print("="*60)
            
            if 'error' in data:
                print(f"\nError: {data['error']}")
            if 'message' in data:
                print(f"Message: {data['message']}")
                
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server")
        print(f"Make sure the Django server is running on {BASE_URL}")
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON response from server")
        print(f"Response text: {response.text}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

def test_invalid_credentials():
    """Test login with invalid credentials"""
    
    print("\n\n" + "="*60)
    print("TESTING INVALID CREDENTIALS")
    print("="*60 + "\n")
    
    credentials = {
        'email': 'admin@mobilefleet.local',
        'password': 'WrongPassword'
    }
    
    try:
        response = requests.post(
            API_LOGIN_ENDPOINT,
            json=credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 401:
            print("\n✓ Invalid credentials properly rejected")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    test_mobile_login()
    test_invalid_credentials()
