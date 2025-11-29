from monitoring.firebase_service import firebase_service

# Debug script to replicate trip_list driver filtering logic

def run_debug(driver_filter='', driver_name_query=''):
    print('DEBUG FILTER RUN')
    print('driver_filter=', driver_filter)
    print('driver_name_query=', driver_name_query)

    # load trips
    trips = firebase_service.get_all_trips()
    print('Total trips loaded:', len(trips))

    # build driver_name_ids
    driver_name_ids = set()
    if driver_name_query:
        all_drivers = firebase_service.get_all_drivers()
        for d in all_drivers:
            name = (d.get('name') or '').lower()
            normalized_id = d.get('driver_id') or d.get('id') or d.get('auth_uid') or (d.get('email') or '').lower()
            if driver_name_query.lower() in name and normalized_id:
                driver_name_ids.add(normalized_id)
    print('driver_name_ids resolved:', driver_name_ids)

    df = str(driver_filter).strip().lower() if driver_filter else ''

    def driver_matches(trip):
        for key in ('driver_id', 'driver', 'driver_name', 'assigned_driver'):
            val = trip.get(key)
            if not val:
                continue
            sval = str(val).strip().lower()
            if df:
                if sval == df:
                    return True
                if df in sval or sval in df:
                    return True
            if trip.get('driver_id') and str(trip.get('driver_id')) in driver_name_ids:
                return True
            if driver_name_query:
                if driver_name_query.lower() in sval:
                    return True
        return False

    matched = [t for t in trips if driver_matches(t)]
    print('Matched trips:', len(matched))
    for t in matched[:10]:
        print(' -', t.get('id'), t.get('driver_id'), t.get('status'), t.get('driver_name'))

if __name__ == '__main__':
    # Example runs
    run_debug('78QY0GtBlEZ34naMQogO', '')
    print('\n')
    run_debug('DRV001', '')
    print('\n')
    run_debug('', 'Maria')
