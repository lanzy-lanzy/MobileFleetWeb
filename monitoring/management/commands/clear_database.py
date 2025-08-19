from django.core.management.base import BaseCommand
from monitoring.firebase_service import firebase_service

class Command(BaseCommand):
    help = 'Clear all data from Firebase Firestore database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  This will delete ALL data from Firebase!\n"
                    "Use --confirm flag to proceed: python manage.py clear_database --confirm"
                )
            )
            return

        self.stdout.write("🗑️  Clearing Firebase database...")
        self.stdout.write("=" * 50)

        try:
            # Get all data first
            terminals = firebase_service.get_all_terminals()
            drivers = firebase_service.get_all_drivers()
            trips = firebase_service.get_all_trips()

            self.stdout.write(f"Found {len(terminals)} terminals, {len(drivers)} drivers, {len(trips)} trips")

            # Clear trips first (they reference drivers and terminals)
            self.stdout.write("\n1. Clearing trips...")
            trip_count = 0
            for trip in trips:
                if firebase_service.delete_trip(trip['trip_id']):
                    trip_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {trip_count} trips"))

            # Clear drivers
            self.stdout.write("\n2. Clearing drivers...")
            driver_count = 0
            for driver in drivers:
                if firebase_service.delete_driver(driver['driver_id']):
                    driver_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {driver_count} drivers"))

            # Clear terminals
            self.stdout.write("\n3. Clearing terminals...")
            terminal_count = 0
            for terminal in terminals:
                if firebase_service.delete_terminal(terminal['terminal_id']):
                    terminal_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {terminal_count} terminals"))

            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("🎉 Database cleared successfully!"))
            self.stdout.write(f"📊 Total deleted: {terminal_count} terminals, {driver_count} drivers, {trip_count} trips")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error clearing database: {e}"))