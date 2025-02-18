import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from base.models import PropertyListing

class Command(BaseCommand):
    help = 'Load property listings from a CSV file'

    def handle(self, *args, **kwargs):
        with open('base/management/commands/properties.csv', mode='r') as file:
            csv_reader = csv.DictReader(file)
            count = 0  # Initialize a counter to limit to the first 5 records
            for row in csv_reader:
                if count == 1000:
                    break  # Stop processing after 5 records
                
                # Safely handle decimal fields with error handling
                def safe_decimal(value):
                    if value in ('N/A', '', 'NA', 'n/a', 'None'):  # Handle missing or invalid data
                        return Decimal('0.0')  # Default to 0.0 if value is missing or invalid
                    try:
                        # Clean the value by removing commas and extra spaces
                        clean_value = value.replace(',', '').strip()
                        return Decimal(clean_value) if clean_value else Decimal('0.0')
                    except InvalidOperation:
                        # Return 0.0 if conversion fails
                        return Decimal('0.0')

                property_listing = PropertyListing(
                    propertyType=row['Type of Property'],
                    location=row['Area Name'],
                    address=row['Location'],
                    floors=int(row['floors']) if row['floors'].isdigit() else 0,
                    coveredArea=row['Covered Area'],
                    electricityStatus=row['Electricity Status'],
                    bathroomCount=int(row['Bathroom']) if row['Bathroom'].isdigit() else 0,
                    bedroomCount=int(row['bedroom']) if row['bedroom'].isdigit() else 0,
                    bookingAmount=safe_decimal(row['Booking Amount']),
                    price=safe_decimal(row['Price']),
                    status=row['Possession Status'],
                )
                property_listing.save()
                count += 1  # Increment the counter

        self.stdout.write(self.style.SUCCESS('Successfully loaded first 1000 property listings'))
