from django.core.management.base import BaseCommand
from monitoring.firebase_service import firebase_service

class Command(BaseCommand):
    help = 'Debug driver-trip filtering logic'

    def add_arguments(self, parser):
        parser.add_argument('--driver_id', type=str, default='')
        parser.add_argument('--driver_name', type=str, default='')

    def handle(self, *args, **options):
        driver_filter = options['driver_id']
        driver_name_query = options['driver_name']

        self.stdout.write('DEBUG FILTER RUN')
        self.stdout.write(f'driver_filter={driver_filter}')
        self.stdout.write(f'driver_name_query={driver_name_query}')

        trips = firebase_service.get_all_trips()
        self.stdout.write(f'Total trips loaded: {len(trips)}')

        driver_name_ids = set()
        if driver_name_query:
            all_drivers = firebase_service.get_all_drivers()
            for d in all_drivers:
                name = (d.get('name') or '').lower()
                normalized_id = d.get('driver_id') or d.get('id') or d.get('auth_uid') or (d.get('email') or '').lower()
                if driver_name_query.lower() in name and normalized_id:
                    driver_name_ids.add(normalized_id)
        self.stdout.write(f'driver_name_ids resolved: {driver_name_ids}')

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
        self.stdout.write(f'Matched trips: {len(matched)}')
        for t in matched[:20]:
            self.stdout.write(f" - {t.get('id')} {t.get('driver_id')} {t.get('status')} {t.get('driver_name')}")
