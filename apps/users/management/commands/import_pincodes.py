from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import Pincode
import csv
import os


class Command(BaseCommand):
    help = 'Import Indian pincodes from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to CSV file containing pincode data',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Create sample pincodes for testing',
        )

    def handle(self, *args, **options):
        if options['sample']:
            self.create_sample_pincodes()
        elif options['file']:
            self.import_from_csv(options['file'])
        else:
            self.stdout.write(self.style.ERROR('Please provide --file or --sample flag'))

    def create_sample_pincodes(self):
        """Create sample pincodes for major Indian cities"""
        self.stdout.write('Creating sample pincodes...')

        sample_pincodes = [
            # Delhi
            {'pincode': '110001', 'area': 'Connaught Place', 'district': 'Central Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110002', 'area': 'Daryaganj', 'district': 'Central Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110003', 'area': 'Kamla Nagar', 'district': 'North Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110005', 'area': 'Karol Bagh', 'district': 'Central Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110016', 'area': 'Lajpat Nagar', 'district': 'South Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110019', 'area': 'Defence Colony', 'district': 'South Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110025', 'area': 'Hauz Khas', 'district': 'South Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110030', 'area': 'Kirti Nagar', 'district': 'West Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110044', 'area': 'Pitampura', 'district': 'North West Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},
            {'pincode': '110048', 'area': 'Rohini', 'district': 'North West Delhi', 'city': 'Delhi', 'state': 'Delhi', 'delivery_days': 1},

            # Mumbai
            {'pincode': '400001', 'area': 'Fort', 'district': 'Mumbai City', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400002', 'area': 'Kalbadevi', 'district': 'Mumbai City', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400003', 'area': 'Masjid Bunder', 'district': 'Mumbai City', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400012', 'area': 'Parel', 'district': 'Mumbai City', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400026', 'area': 'Bandra', 'district': 'Mumbai Suburban', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400049', 'area': 'Andheri West', 'district': 'Mumbai Suburban', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400050', 'area': 'Bandra West', 'district': 'Mumbai Suburban', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400051', 'area': 'Juhu', 'district': 'Mumbai Suburban', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400059', 'area': 'Goregaon West', 'district': 'Mumbai Suburban', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '400101', 'area': 'Borivali', 'district': 'Mumbai Suburban', 'city': 'Mumbai', 'state': 'Maharashtra', 'delivery_days': 2},

            # Bangalore
            {'pincode': '560001', 'area': 'MG Road', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560002', 'area': 'Shivajinagar', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560003', 'area': 'Basavanagudi', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560004', 'area': 'Malleshwaram', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560017', 'area': 'Rajajinagar', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560034', 'area': 'Indiranagar', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560066', 'area': 'Whitefield', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560076', 'area': 'HSR Layout', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560095', 'area': 'Marathahalli', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},
            {'pincode': '560100', 'area': 'Electronic City', 'district': 'Bangalore Urban', 'city': 'Bangalore', 'state': 'Karnataka', 'delivery_days': 2},

            # Hyderabad
            {'pincode': '500001', 'area': 'Charminar', 'district': 'Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'delivery_days': 2},
            {'pincode': '500003', 'area': 'Kachiguda', 'district': 'Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'delivery_days': 2},
            {'pincode': '500016', 'area': 'Himayatnagar', 'district': 'Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'delivery_days': 2},
            {'pincode': '500018', 'area': 'Banjara Hills', 'district': 'Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'delivery_days': 2},
            {'pincode': '500081', 'area': 'Gachibowli', 'district': 'Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'delivery_days': 2},

            # Chennai
            {'pincode': '600001', 'area': 'Parrys', 'district': 'Chennai', 'city': 'Chennai', 'state': 'Tamil Nadu', 'delivery_days': 2},
            {'pincode': '600002', 'area': 'Anna Salai', 'district': 'Chennai', 'city': 'Chennai', 'state': 'Tamil Nadu', 'delivery_days': 2},
            {'pincode': '600017', 'area': 'T Nagar', 'district': 'Chennai', 'city': 'Chennai', 'state': 'Tamil Nadu', 'delivery_days': 2},
            {'pincode': '600020', 'area': 'Mylapore', 'district': 'Chennai', 'city': 'Chennai', 'state': 'Tamil Nadu', 'delivery_days': 2},
            {'pincode': '600028', 'area': 'Adyar', 'district': 'Chennai', 'city': 'Chennai', 'state': 'Tamil Nadu', 'delivery_days': 2},

            # Pune
            {'pincode': '411001', 'area': 'Pune City', 'district': 'Pune', 'city': 'Pune', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '411004', 'area': 'Shivajinagar', 'district': 'Pune', 'city': 'Pune', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '411008', 'area': 'Kothrud', 'district': 'Pune', 'city': 'Pune', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '411038', 'area': 'Hinjewadi', 'district': 'Pune', 'city': 'Pune', 'state': 'Maharashtra', 'delivery_days': 2},
            {'pincode': '411048', 'area': 'Hadapsar', 'district': 'Pune', 'city': 'Pune', 'state': 'Maharashtra', 'delivery_days': 2},

            # Kolkata
            {'pincode': '700001', 'area': 'BBD Bagh', 'district': 'Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'delivery_days': 2},
            {'pincode': '700019', 'area': 'Alipore', 'district': 'Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'delivery_days': 2},
            {'pincode': '700027', 'area': 'Park Street', 'district': 'Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'delivery_days': 2},
            {'pincode': '700068', 'area': 'Salt Lake', 'district': 'Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'delivery_days': 2},

            # Ahmedabad
            {'pincode': '380001', 'area': 'Lal Darwaja', 'district': 'Ahmedabad', 'city': 'Ahmedabad', 'state': 'Gujarat', 'delivery_days': 2},
            {'pincode': '380009', 'area': 'Navrangpura', 'district': 'Ahmedabad', 'city': 'Ahmedabad', 'state': 'Gujarat', 'delivery_days': 2},
            {'pincode': '380015', 'area': 'Satellite', 'district': 'Ahmedabad', 'city': 'Ahmedabad', 'state': 'Gujarat', 'delivery_days': 2},

            # Jaipur
            {'pincode': '302001', 'area': 'MI Road', 'district': 'Jaipur', 'city': 'Jaipur', 'state': 'Rajasthan', 'delivery_days': 3},
            {'pincode': '302017', 'area': 'Mansarovar', 'district': 'Jaipur', 'city': 'Jaipur', 'state': 'Rajasthan', 'delivery_days': 3},

            # Chandigarh
            {'pincode': '160001', 'area': 'Sector 1', 'district': 'Chandigarh', 'city': 'Chandigarh', 'state': 'Chandigarh', 'delivery_days': 2},
            {'pincode': '160017', 'area': 'Sector 17', 'district': 'Chandigarh', 'city': 'Chandigarh', 'state': 'Chandigarh', 'delivery_days': 2},
        ]

        with transaction.atomic():
            created_count = 0
            for pincode_data in sample_pincodes:
                pincode, created = Pincode.objects.get_or_create(
                    pincode=pincode_data['pincode'],
                    defaults={
                        'area': pincode_data['area'],
                        'district': pincode_data['district'],
                        'city': pincode_data['city'],
                        'state': pincode_data['state'],
                        'delivery_days': pincode_data['delivery_days'],
                        'is_serviceable': True,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'Created: {pincode.pincode} - {pincode.area}, {pincode.city}')
                else:
                    self.stdout.write(f'Already exists: {pincode.pincode}')

        self.stdout.write(self.style.SUCCESS(f'Sample pincodes created successfully! Total: {created_count}'))

    def import_from_csv(self, file_path):
        """
        Import pincodes from CSV file
        Expected CSV format: pincode,area,district,city,state,delivery_days
        """
        self.stdout.write(f'Importing pincodes from {file_path}...')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            with transaction.atomic():
                created_count = 0
                updated_count = 0

                for row in reader:
                    pincode = row.get('pincode', '').strip()
                    if not pincode or len(pincode) != 6:
                        continue

                    pincode_obj, created = Pincode.objects.update_or_create(
                        pincode=pincode,
                        defaults={
                            'area': row.get('area', '').strip(),
                            'district': row.get('district', '').strip(),
                            'city': row.get('city', '').strip(),
                            'state': row.get('state', '').strip(),
                            'delivery_days': int(row.get('delivery_days', 3)),
                            'is_serviceable': row.get('is_serviceable', 'true').lower() == 'true',
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    if (created_count + updated_count) % 100 == 0:
                        self.stdout.write(f'Processed {created_count + updated_count} pincodes...')

        self.stdout.write(self.style.SUCCESS(
            f'Import complete! Created: {created_count}, Updated: {updated_count}'
        ))
