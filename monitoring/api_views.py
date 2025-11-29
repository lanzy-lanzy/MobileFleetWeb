"""
Mobile App API Views for Firebase Integration
Handles trip start/stop, passenger tracking, and QR code scanning
"""

import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate
from .firebase_service import firebase_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def mobile_login(request):
    """
    Mobile app login endpoint
    Authenticates user and returns driver information
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({
                'error': 'Email and password are required'
            }, status=400)
        
        # Authenticate using email (username in Django)
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return JsonResponse({
                'error': 'Invalid email or password'
            }, status=401)
        
        # Find driver linked to this user email
        drivers = firebase_service.get_all_drivers()
        driver = None
        
        for d in drivers:
            if d.get('email') == email:
                driver = d
                break
        
        if not driver:
            return JsonResponse({
                'error': 'No authenticated driver found',
                'user_authenticated': True,
                'message': 'User account exists but no driver profile found. Please contact administrator.'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'driver': driver,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name
            },
            'message': 'Login successful'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error during mobile login: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def scan_qr_code(request):
    """
    Handle QR code scanning from mobile app
    Validates terminal and returns terminal information
    """
    try:
        data = json.loads(request.body)
        qr_code = data.get('qr_code')
        
        if not qr_code:
            return JsonResponse({'error': 'QR code is required'}, status=400)
        
        # Find terminal by QR code
        terminals = firebase_service.get_all_terminals()
        terminal = None
        
        for t in terminals:
            if t.get('qr_code') == qr_code:
                terminal = t
                break
        
        if not terminal:
            return JsonResponse({'error': 'Invalid QR code'}, status=404)
        
        return JsonResponse({
            'success': True,
            'terminal': {
                'terminal_id': terminal.get('terminal_id'),
                'name': terminal.get('name'),
                'latitude': terminal.get('latitude'),
                'longitude': terminal.get('longitude'),
                'is_active': terminal.get('is_active', True)
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error scanning QR code: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_trip(request):
    """
    Start a new trip from mobile app
    Creates trip record with initial passenger count
    """
    try:
        data = json.loads(request.body)
        
        # Required fields
        driver_id = data.get('driver_id')
        start_terminal = data.get('start_terminal')
        destination_terminal = data.get('destination_terminal')
        passengers = data.get('passengers', 0)
        
        if not all([driver_id, start_terminal, destination_terminal]):
            return JsonResponse({
                'error': 'driver_id, start_terminal, and destination_terminal are required'
            }, status=400)
        
        # Validate driver exists
        driver = firebase_service.get_driver(driver_id)
        if not driver:
            return JsonResponse({'error': 'Driver not found'}, status=404)
        
        # Validate terminals exist
        start_term = firebase_service.get_terminal(start_terminal)
        dest_term = firebase_service.get_terminal(destination_terminal)
        
        if not start_term:
            return JsonResponse({'error': 'Start terminal not found'}, status=404)
        if not dest_term:
            return JsonResponse({'error': 'Destination terminal not found'}, status=404)
        
        # Create trip data
        trip_data = {
            'driver_id': driver_id,
            'start_terminal': start_terminal,
            'destination_terminal': destination_terminal,
            'passengers': int(passengers),
            'status': 'in_progress',
            'start_time': datetime.now(),
            'arrival_time': None,
        }
        
        # Create trip in Firebase
        trip_id = firebase_service.create_trip(trip_data)
        
        if trip_id:
            # Get the created trip data
            created_trip = firebase_service.get_trip(trip_id)
            
            return JsonResponse({
                'success': True,
                'trip_id': trip_id,
                'trip': created_trip,
                'message': 'Trip started successfully'
            })
        else:
            return JsonResponse({'error': 'Failed to create trip'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error starting trip: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_trip_passengers(request, trip_id):
    """
    Update passenger count for an active trip
    """
    try:
        data = json.loads(request.body)
        passengers = data.get('passengers')
        
        if passengers is None:
            return JsonResponse({'error': 'passengers field is required'}, status=400)
        
        # Validate trip exists and is active
        trip = firebase_service.get_trip(trip_id)
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)
        
        if trip.get('status') != 'in_progress':
            return JsonResponse({'error': 'Trip is not active'}, status=400)
        
        # Update passenger count
        update_data = {
            'passengers': int(passengers)
        }
        
        success = firebase_service.update_trip(trip_id, update_data)
        
        if success:
            # Get updated trip data
            updated_trip = firebase_service.get_trip(trip_id)
            
            return JsonResponse({
                'success': True,
                'trip': updated_trip,
                'message': 'Passenger count updated successfully'
            })
        else:
            return JsonResponse({'error': 'Failed to update trip'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid passenger count'}, status=400)
    except Exception as e:
        logger.error(f"Error updating trip passengers: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def stop_trip(request, trip_id):
    """
    Stop/complete a trip from mobile app
    Sets arrival time and marks trip as completed
    """
    try:
        data = json.loads(request.body)
        
        # Validate trip exists and is active
        trip = firebase_service.get_trip(trip_id)
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)
        
        if trip.get('status') != 'in_progress':
            return JsonResponse({'error': 'Trip is not active'}, status=400)
        
        # Update trip to completed
        update_data = {
            'status': 'completed',
            'arrival_time': datetime.now()
        }
        
        # Include final passenger count if provided
        final_passengers = data.get('passengers')
        if final_passengers is not None:
            update_data['passengers'] = int(final_passengers)
        
        success = firebase_service.update_trip(trip_id, update_data)
        
        if success:
            # Get updated trip data
            updated_trip = firebase_service.get_trip(trip_id)
            
            return JsonResponse({
                'success': True,
                'trip': updated_trip,
                'message': 'Trip completed successfully'
            })
        else:
            return JsonResponse({'error': 'Failed to complete trip'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid passenger count'}, status=400)
    except Exception as e:
        logger.error(f"Error stopping trip: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def get_active_trips_api(request):
    """
    Get all active trips for mobile app
    """
    try:
        driver_id = request.GET.get('driver_id')
        
        if driver_id:
            # Get trips for specific driver
            trips = firebase_service.get_trips_by_driver(driver_id)
            # Filter only active trips
            active_trips = [trip for trip in trips if trip.get('status') == 'in_progress']
        else:
            # Get all active trips
            active_trips = firebase_service.get_active_trips()
        
        return JsonResponse({
            'success': True,
            'trips': active_trips,
            'count': len(active_trips)
        })
        
    except Exception as e:
        logger.error(f"Error getting active trips: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def get_trip_details(request, trip_id):
    """
    Get detailed information about a specific trip
    """
    try:
        trip = firebase_service.get_trip(trip_id)
        
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)
        
        # Get additional details
        driver = firebase_service.get_driver(trip.get('driver_id'))
        start_terminal = firebase_service.get_terminal(trip.get('start_terminal'))
        dest_terminal = firebase_service.get_terminal(trip.get('destination_terminal'))
        
        return JsonResponse({
            'success': True,
            'trip': trip,
            'driver': driver,
            'start_terminal': start_terminal,
            'destination_terminal': dest_terminal
        })
        
    except Exception as e:
        logger.error(f"Error getting trip details: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def get_driver_info(request, driver_id):
    """
    Get driver information for mobile app
    """
    try:
        driver = firebase_service.get_driver(driver_id)
        
        if not driver:
            return JsonResponse({'error': 'Driver not found'}, status=404)
        
        # Get driver's active trips
        driver_trips = firebase_service.get_trips_by_driver(driver_id)
        active_trips = [trip for trip in driver_trips if trip.get('status') == 'in_progress']
        
        return JsonResponse({
            'success': True,
            'driver': driver,
            'active_trips': active_trips,
            'active_trip_count': len(active_trips)
        })
        
    except Exception as e:
        logger.error(f"Error getting driver info: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
