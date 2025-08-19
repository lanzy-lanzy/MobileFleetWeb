from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Clear database and repopulate with sample data including QR codes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to reset all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  This will DELETE ALL data and repopulate with sample data!\n"
                    "Use --confirm flag to proceed: python manage.py reset_with_qr --confirm"
                )
            )
            return

        self.stdout.write("🔄 Resetting database with QR codes...")
        self.stdout.write("=" * 60)

        # Check Cloudinary configuration
        cloudinary_config = getattr(settings, 'CLOUDINARY_CONFIG', {})
        cloudinary_configured = all([
            cloudinary_config.get('cloud_name', '').replace('your-cloudinary-cloud-name', ''),
            cloudinary_config.get('api_key', '').replace('your-cloudinary-api-key', ''),
            cloudinary_config.get('api_secret', '').replace('your-cloudinary-api-secret', ''),
        ])

        if not cloudinary_configured:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Cloudinary credentials not configured!\n"
                    "QR codes will not be generated. Please update your .env file with:\n"
                    "CLOUDINARY_CLOUD_NAME=your-actual-cloud-name\n"
                    "CLOUDINARY_API_KEY=your-actual-api-key\n"
                    "CLOUDINARY_API_SECRET=your-actual-api-secret"
                )
            )
            generate_qr = False
        else:
            self.stdout.write(self.style.SUCCESS("✅ Cloudinary configured - QR codes will be generated"))
            generate_qr = True

        try:
            # Step 1: Clear existing data
            self.stdout.write("\n🗑️  Step 1: Clearing existing data...")
            call_command('clear_database', '--confirm')

            # Step 2: Populate with new data
            self.stdout.write("\n🚀 Step 2: Populating with sample data...")
            if generate_qr:
                call_command('populate_sample_data', '--with-qr')
            else:
                call_command('populate_sample_data')

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("🎉 Database reset completed successfully!"))

            if generate_qr:
                self.stdout.write(self.style.SUCCESS("📱 QR codes have been generated and uploaded to Cloudinary"))
            else:
                self.stdout.write(self.style.WARNING("📱 QR codes were not generated (Cloudinary not configured)"))

            self.stdout.write("\n🌐 Visit http://localhost:8000/ to see the new data!")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during reset: {e}"))