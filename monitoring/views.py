from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
from .firebase_service import firebase_service
from .utils import generate_and_upload_qr, get_qr_code_base64
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'monitoring/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required(login_url='login')
def home(request):
    """Dashboard home page"""
    try:
        # Get summary statistics
        terminals = firebase_service.get_all_terminals()
        drivers = firebase_service.get_all_drivers()
        active_trips = firebase_service.get_active_trips()
        completed_trips = firebase_service.get_completed_trips()

        # Get recent trips and resolve terminal names
        recent_trips = firebase_service.get_all_trips(limit=10)

        # Create a mapping of terminal IDs to names for quick lookup
        terminal_map = {terminal.get('terminal_id', terminal.get('id')): terminal.get('name', 'Unknown Terminal')
                       for terminal in terminals}

        # Resolve terminal names in recent trips
        for trip in recent_trips:
            start_terminal_id = trip.get('start_terminal')
            destination_terminal_id = trip.get('destination_terminal')

            # Add resolved terminal names to trip data
            trip['start_terminal_name'] = terminal_map.get(start_terminal_id, start_terminal_id or 'Unknown')
            trip['destination_terminal_name'] = terminal_map.get(destination_terminal_id, destination_terminal_id or 'Unknown')

        context = {
            'total_terminals': len(terminals),
            'total_drivers': len(drivers),
            'active_trips': len(active_trips),
            'completed_trips': len(completed_trips),
            'recent_trips': recent_trips,
            'firebase_project_id': settings.FIREBASE_PROJECT_ID,
        }
        return render(request, 'monitoring/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        messages.error(request, "Error loading dashboard data")
        return render(request, 'monitoring/dashboard.html', {'error': str(e)})


@login_required(login_url='login')
def firebase_config(request):
    """Provide Firebase configuration for frontend"""
    # For the actual Firebase web config, you would get these values from Firebase Console
    # Go to Project Settings > General > Your apps > Web app > Config
    # For now, using the project ID we have and placeholder values
    config = {
        'apiKey': 'AIzaSyBvOoM5xgOJYhZlXQZ8fJ9X2nY3kL4mP6Q',  # Replace with actual API key from Firebase Console
        'authDomain': f'{settings.FIREBASE_PROJECT_ID}.firebaseapp.com',
        'projectId': settings.FIREBASE_PROJECT_ID,
        'storageBucket': f'{settings.FIREBASE_PROJECT_ID}.appspot.com',
        'messagingSenderId': '123456789012',  # Replace with actual sender ID from Firebase Console
        'appId': '1:123456789012:web:abcdef123456789012345678'  # Replace with actual app ID from Firebase Console
    }
    return JsonResponse(config)


# Terminal Management Views
@login_required(login_url='login')
def terminal_list(request):
    """List all terminals"""
    try:
        terminals = firebase_service.get_all_terminals()

        # Pagination
        paginator = Paginator(terminals, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'terminals': page_obj,
            'page_obj': page_obj,
        }
        return render(request, 'monitoring/terminals/list.html', context)
    except Exception as e:
        logger.error(f"Error loading terminals: {e}")
        messages.error(request, "Error loading terminals")
        return render(request, 'monitoring/terminals/list.html', {'terminals': []})

@login_required(login_url='login')
def terminal_create(request):
    """Create a new terminal"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            if not name:
                messages.error(request, "Terminal name is required")
                return render(request, 'monitoring/terminals/create.html')

            # Create terminal data
            terminal_data = {
                'name': name,
                'latitude': float(latitude) if latitude else None,
                'longitude': float(longitude) if longitude else None,
                'is_active': True,
            }

            # Create terminal in Firebase
            terminal_id = firebase_service.create_terminal(terminal_data)

            if terminal_id:
                # Generate and upload QR code
                qr_url = generate_and_upload_qr(terminal_id, name)
                if qr_url:
                    firebase_service.update_terminal(terminal_id, {'qr_code_url': qr_url})

                messages.success(request, f"Terminal '{name}' created successfully")
                return redirect('terminal_list')
            else:
                messages.error(request, "Failed to create terminal")
        except Exception as e:
            logger.error(f"Error creating terminal: {e}")
            messages.error(request, f"Error creating terminal: {str(e)}")

    return render(request, 'monitoring/terminals/create.html')

@login_required(login_url='login')
def terminal_detail(request, terminal_id):
    """View terminal details"""
    try:
        terminal = firebase_service.get_terminal(terminal_id)
        if not terminal:
            messages.error(request, "Terminal not found")
            return redirect('terminal_list')

        # Generate QR code for display
        qr_data = f"terminal_id:{terminal_id}"
        qr_base64 = get_qr_code_base64(qr_data)

        context = {
            'terminal': terminal,
            'terminal_id': terminal_id,
            'qr_base64': qr_base64,
        }
        return render(request, 'monitoring/terminals/detail.html', context)
    except Exception as e:
        logger.error(f"Error loading terminal {terminal_id}: {e}")
        messages.error(request, "Error loading terminal details")
        return redirect('terminal_list')

@login_required(login_url='login')
def terminal_edit(request, terminal_id):
    """Edit terminal"""
    try:
        terminal = firebase_service.get_terminal(terminal_id)
        if not terminal:
            messages.error(request, "Terminal not found")
            return redirect('terminal_list')

        if request.method == 'POST':
            name = request.POST.get('name')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            is_active = request.POST.get('is_active') == 'on'

            if not name:
                messages.error(request, "Terminal name is required")
                return render(request, 'monitoring/terminals/edit.html', {'terminal': terminal})

            # Update terminal data
            update_data = {
                'name': name,
                'latitude': float(latitude) if latitude else None,
                'longitude': float(longitude) if longitude else None,
                'is_active': is_active,
            }

            # Update terminal in Firebase
            if firebase_service.update_terminal(terminal_id, update_data):
                messages.success(request, f"Terminal '{name}' updated successfully")
                return redirect('terminal_detail', terminal_id=terminal_id)
            else:
                messages.error(request, "Failed to update terminal")

        context = {
            'terminal': terminal,
            'terminal_id': terminal_id,
        }
        return render(request, 'monitoring/terminals/edit.html', context)
    except Exception as e:
        logger.error(f"Error editing terminal {terminal_id}: {e}")
        messages.error(request, "Error editing terminal")
        return redirect('terminal_list')

@login_required(login_url='login')
def terminal_delete(request, terminal_id):
    """Delete terminal"""
    if request.method == 'POST':
        try:
            terminal = firebase_service.get_terminal(terminal_id)
            if not terminal:
                messages.error(request, "Terminal not found")
                return redirect('terminal_list')

            if firebase_service.delete_terminal(terminal_id):
                messages.success(request, f"Terminal '{terminal['name']}' deleted successfully")
            else:
                messages.error(request, "Failed to delete terminal")
        except Exception as e:
            logger.error(f"Error deleting terminal {terminal_id}: {e}")
            messages.error(request, "Error deleting terminal")

    return redirect('terminal_list')

# Driver Management Views
@login_required(login_url='login')
def driver_list(request):
    """List all drivers"""
    try:
        drivers = firebase_service.get_all_drivers()

        # Pagination
        paginator = Paginator(drivers, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'drivers': page_obj,
            'page_obj': page_obj,
        }
        return render(request, 'monitoring/drivers/list.html', context)
    except Exception as e:
        logger.error(f"Error loading drivers: {e}")
        messages.error(request, "Error loading drivers")
        return render(request, 'monitoring/drivers/list.html', {'drivers': []})

@login_required(login_url='login')
def driver_create(request):
    """Create a new driver with Firebase Auth and Django User"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            contact = request.POST.get('contact')
            license_number = request.POST.get('license_number')

            # Validate required fields
            if not name or not email or not password:
                messages.error(request, "Name, email, and password are required")
                return render(request, 'monitoring/drivers/create.html')

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f"A user with email '{email}' already exists")
                return render(request, 'monitoring/drivers/create.html')

            # Create Django User Account first (required for mobile app login)
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )
                logger.info(f"Created Django user account for {email}")
            except Exception as e:
                logger.error(f"Error creating Django user: {e}")
                messages.error(request, f"Failed to create user account: {str(e)}")
                return render(request, 'monitoring/drivers/create.html')

            # Create Firebase Auth user
            auth_uid = firebase_service.create_auth_user(email, password, name)
            
            if not auth_uid:
                # Delete the Django user if Firebase creation fails
                user.delete()
                messages.error(request, "Failed to create Firebase authentication. Email may already be in use.")
                return render(request, 'monitoring/drivers/create.html')

            # Create driver data with auth_uid and Django user id
            driver_data = {
                'name': name,
                'email': email,
                'contact': contact or '',
                'license_number': license_number or '',
                'is_active': True,
                'auth_uid': auth_uid,  # Link to Firebase Auth
                'django_user_id': user.id,  # Link to Django User
            }

            # Create driver in Firebase
            driver_id = firebase_service.create_driver(driver_data)

            if driver_id:
                messages.success(request, f"Driver '{name}' created successfully. Can now login with email: {email}")
                return redirect('driver_list')
            else:
                # Delete user and log error if driver creation fails
                user.delete()
                messages.error(request, "Failed to create driver record in database")
        except Exception as e:
            logger.error(f"Error creating driver: {e}")
            messages.error(request, f"Error creating driver: {str(e)}")

    return render(request, 'monitoring/drivers/create.html')

@login_required(login_url='login')
def driver_detail(request, driver_id):
    """View driver details"""
    try:
        driver = firebase_service.get_driver(driver_id)
        if not driver:
            messages.error(request, "Driver not found")
            return redirect('driver_list')

        # Get driver's trips
        driver_trips = firebase_service.get_trips_by_driver(driver_id)

        context = {
            'driver': driver,
            'driver_id': driver_id,
            'driver_trips': driver_trips,
        }
        return render(request, 'monitoring/drivers/detail.html', context)
    except Exception as e:
        logger.error(f"Error loading driver {driver_id}: {e}")
        messages.error(request, "Error loading driver details")
        return redirect('driver_list')

@login_required(login_url='login')
def driver_edit(request, driver_id):
    """Edit driver"""
    try:
        driver = firebase_service.get_driver(driver_id)
        if not driver:
            messages.error(request, "Driver not found")
            return redirect('driver_list')

        if request.method == 'POST':
            name = request.POST.get('name')
            contact = request.POST.get('contact')
            license_number = request.POST.get('license_number')
            is_active = request.POST.get('is_active') == 'on'

            if not name:
                messages.error(request, "Driver name is required")
                return render(request, 'monitoring/drivers/edit.html', {'driver': driver})

            # Update driver data
            update_data = {
                'name': name,
                'contact': contact or '',
                'license_number': license_number or '',
                'is_active': is_active,
            }

            # Update driver in Firebase
            if firebase_service.update_driver(driver_id, update_data):
                messages.success(request, f"Driver '{name}' updated successfully")
                return redirect('driver_detail', driver_id=driver_id)
            else:
                messages.error(request, "Failed to update driver")

        context = {
            'driver': driver,
            'driver_id': driver_id,
        }
        return render(request, 'monitoring/drivers/edit.html', context)
    except Exception as e:
        logger.error(f"Error editing driver {driver_id}: {e}")
        messages.error(request, "Error editing driver")
        return redirect('driver_list')

@login_required(login_url='login')
def driver_delete(request, driver_id):
    """Delete driver"""
    if request.method == 'POST':
        try:
            driver = firebase_service.get_driver(driver_id)
            if not driver:
                messages.error(request, "Driver not found")
                return redirect('driver_list')

            if firebase_service.delete_driver(driver_id):
                messages.success(request, f"Driver '{driver['name']}' deleted successfully")
            else:
                messages.error(request, "Failed to delete driver")
        except Exception as e:
            logger.error(f"Error deleting driver {driver_id}: {e}")
            messages.error(request, "Error deleting driver")

    return redirect('driver_list')

# Trip Management Views
@login_required(login_url='login')
def trip_list(request):
    """List all trips with filtering"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', 'all')
        driver_filter = request.GET.get('driver', '')
        # New: allow searching by driver name (partial match). This parameter
        # is used by the frontend keyup search. If provided, we'll resolve it
        # to matching driver_ids or fall back to matching trip.driver_name.
        driver_name_query = request.GET.get('driver_name', '').strip()

        # Get the current user's driver record to auto-filter their trips
        current_user = request.user
        user_driver = None
        auto_filter_driver = False
        
        # Try to find the driver associated with the current user
        try:
            drivers = firebase_service.get_all_drivers()
            for driver in drivers:
                # Normalize driver identifier for matching
                normalized_id = driver.get('driver_id') or driver.get('id') or driver.get('auth_uid') or (driver.get('email') or '').lower()
                # Ensure the driver record we keep has a normalized driver_id field
                driver['driver_id'] = normalized_id

                # Match by django_user_id or email
                driver_email = driver.get('email', '').lower()
                user_email = current_user.email.lower()
                django_id = driver.get('django_user_id')

                if django_id == current_user.id or driver_email == user_email:
                    user_driver = driver
                    auto_filter_driver = True
                    # Auto-set driver filter if user is a driver and no filter is specified
                    if not driver_filter:
                        driver_filter = normalized_id
                        logger.info(f"Auto-filtering trips for driver {current_user.username} (ID: {normalized_id})")
                    break
        except Exception as e:
            logger.warning(f"Could not find driver for user {current_user.id}: {e}")

        # Get trips based on filter
        if status_filter == 'active':
            trips = firebase_service.get_active_trips()
        elif status_filter == 'completed':
            trips = firebase_service.get_completed_trips()
        elif status_filter == 'cancelled':
            trips = firebase_service.get_trips_by_status('cancelled')
        else:
            trips = firebase_service.get_all_trips()

        # Filter by driver if specified (mandatory for drivers viewing their own trips)
        # Prepare driver_name based filtering: build a set of matching driver ids
        driver_name_ids = set()
        if driver_name_query:
            try:
                all_drivers = firebase_service.get_all_drivers()
                for d in all_drivers:
                    name = (d.get('name') or '').lower()
                    normalized_id = d.get('driver_id') or d.get('id') or d.get('auth_uid') or (d.get('email') or '').lower()
                    if driver_name_query.lower() in name and normalized_id:
                        driver_name_ids.add(normalized_id)
            except Exception:
                logger.debug('Could not resolve driver_name to ids')

        if driver_filter or driver_name_ids:
            # Use flexible matching to avoid missing trips due to case differences
            # or slightly different identifier fields between drivers and trips.
            df = str(driver_filter).strip().lower() if driver_filter else ''

            def driver_matches(trip):
                # Check several possible fields that may contain driver identifiers
                for key in ('driver_id', 'driver', 'driver_name', 'assigned_driver'):
                    val = trip.get(key)
                    if not val:
                        continue
                    sval = str(val).strip().lower()
                    # If we have explicit driver filter (id), match against it
                    if df:
                        if sval == df:
                            return True
                        if df in sval or sval in df:
                            return True

                    # If name-based ids were found, match driver_id against them
                    if trip.get('driver_id') and str(trip.get('driver_id')) in driver_name_ids:
                        return True

                    # As fallback, if driver_name_query is present, try matching trip.driver_name
                    if driver_name_query:
                        if driver_name_query.lower() in sval:
                            return True

                return False

            trips = [trip for trip in trips if driver_matches(trip)]

        # Get all drivers and terminals for filter dropdown and name resolution
        drivers = firebase_service.get_all_drivers()

        # Normalize driver IDs so template and server-side filtering use a consistent identifier.
        # Some driver records may have 'driver_id' (created by this app), others may only have 'id',
        # or might use 'auth_uid' or email. Normalize to a single `driver_id` value.
        for driver in drivers:
            normalized = driver.get('driver_id') or driver.get('id') or driver.get('auth_uid') or (driver.get('email') or '').lower()
            driver['driver_id'] = normalized
        terminals = firebase_service.get_all_terminals()

        # Create mappings for quick lookup
        terminal_map = {terminal.get('terminal_id', terminal.get('id')): terminal.get('name', 'Unknown Terminal')
                       for terminal in terminals}
        driver_map = {driver.get('driver_id'): driver.get('name', 'Unknown Driver')
                 for driver in drivers}

        # Resolve terminal and driver names in trips
        for trip in trips:
            start_terminal_id = trip.get('start_terminal')
            destination_terminal_id = trip.get('destination_terminal')
            driver_id = trip.get('driver_id')

            # Add resolved names to trip data
            trip['start_terminal_name'] = terminal_map.get(start_terminal_id, start_terminal_id or 'Unknown')
            trip['destination_terminal_name'] = terminal_map.get(destination_terminal_id, destination_terminal_id or 'Unknown')
            trip['driver_name'] = driver_map.get(driver_id, driver_id or 'Unknown')

        # Ensure dropdown includes any driver identifiers referenced by trips
        # (handles legacy/alias IDs like 'DRV001' that don't have driver docs).
        try:
            all_trips_for_ids = firebase_service.get_all_trips()
            unique_trip_driver_ids = {t.get('driver_id') for t in all_trips_for_ids if t.get('driver_id')}
            for tid in unique_trip_driver_ids:
                if tid and tid not in driver_map:
                    # Add a placeholder driver entry so the dropdown can select this id
                    placeholder = {'driver_id': tid, 'name': f'Unknown Driver ({tid})'}
                    drivers.append(placeholder)
                    driver_map[tid] = placeholder['name']
        except Exception:
            # If Firestore can't be queried here, skip adding placeholders
            logger.debug('Could not load all trips to reconcile missing driver ids')

        # Pagination
        paginator = Paginator(trips, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'trips': page_obj,
            'page_obj': page_obj,
            'drivers': drivers,
            'status_filter': status_filter,
            'driver_filter': driver_filter,
            'is_driver': auto_filter_driver,
            'user_driver': user_driver,
        }

        # Return partial template for HTMX requests
        if request.headers.get('HX-Request'):
            return render(request, 'monitoring/trips/trip_list_partial.html', context)

        return render(request, 'monitoring/trips/list.html', context)
    except Exception as e:
        logger.error(f"Error loading trips: {e}")
        messages.error(request, "Error loading trips")
        return render(request, 'monitoring/trips/list.html', {'trips': [], 'drivers': []})

@login_required(login_url='login')
def trip_detail(request, trip_id):
    """View trip details"""
    try:
        trip = firebase_service.get_trip(trip_id)
        if not trip:
            messages.error(request, "Trip not found")
            return redirect('trip_list')

        # Get related data
        driver = firebase_service.get_driver(trip.get('driver_id', ''))
        start_terminal = firebase_service.get_terminal(trip.get('start_terminal', ''))
        dest_terminal = firebase_service.get_terminal(trip.get('destination_terminal', ''))

        context = {
            'trip': trip,
            'trip_id': trip_id,
            'driver': driver,
            'start_terminal': start_terminal,
            'dest_terminal': dest_terminal,
        }
        return render(request, 'monitoring/trips/detail.html', context)
    except Exception as e:
        logger.error(f"Error loading trip {trip_id}: {e}")
        messages.error(request, "Error loading trip details")
        return redirect('trip_list')

@login_required(login_url='login')
def trip_create(request):
    """Create a new trip (for testing purposes)"""
    if request.method == 'POST':
        try:
            driver_id = request.POST.get('driver_id')
            start_terminal = request.POST.get('start_terminal')
            destination_terminal = request.POST.get('destination_terminal')
            passengers = request.POST.get('passengers', 0)

            if not all([driver_id, start_terminal, destination_terminal]):
                messages.error(request, "All fields are required")
                return render(request, 'monitoring/trips/create.html')

            # Create trip data
            trip_data = {
                'driver_id': driver_id,
                'start_terminal': start_terminal,
                'destination_terminal': destination_terminal,
                'passengers': int(passengers),
                'status': 'in_progress',
                'start_time': None,  # Will be set when driver scans QR
                'arrival_time': None,
            }

            # Create trip in Firebase
            trip_id = firebase_service.create_trip(trip_data)

            if trip_id:
                messages.success(request, "Trip created successfully")
                return redirect('trip_detail', trip_id=trip_id)
            else:
                messages.error(request, "Failed to create trip")
        except Exception as e:
            logger.error(f"Error creating trip: {e}")
            messages.error(request, f"Error creating trip: {str(e)}")

    # Get drivers and terminals for form
    try:
        drivers = firebase_service.get_all_drivers()
        terminals = firebase_service.get_all_terminals()
        context = {
            'drivers': drivers,
            'terminals': terminals,
        }
        return render(request, 'monitoring/trips/create.html', context)
    except Exception as e:
        logger.error(f"Error loading form data: {e}")
        return render(request, 'monitoring/trips/create.html', {'drivers': [], 'terminals': []})

@login_required(login_url='login')
def trip_update_status(request, trip_id):
    """Update trip status (HTMX endpoint)"""
    if request.method == 'POST':
        try:
            new_status = request.POST.get('status')
            if new_status not in ['in_progress', 'completed', 'cancelled']:
                return JsonResponse({'error': 'Invalid status'}, status=400)

            trip = firebase_service.get_trip(trip_id)
            if not trip:
                return JsonResponse({'error': 'Trip not found'}, status=404)

            update_data = {'status': new_status}

            # Set arrival time if completing trip
            if new_status == 'completed' and not trip.get('arrival_time'):
                from datetime import datetime
                update_data['arrival_time'] = datetime.now()

            if firebase_service.update_trip(trip_id, update_data):
                # Return updated trip card for HTMX
                updated_trip = firebase_service.get_trip(trip_id)
                context = {'trip': updated_trip}
                return render(request, 'monitoring/trips/trip_card.html', context)
            else:
                return JsonResponse({'error': 'Failed to update trip'}, status=500)
        except Exception as e:
            logger.error(f"Error updating trip status: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
