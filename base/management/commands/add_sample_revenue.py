from django.core.management.base import BaseCommand
from base.models import Revenue
from decimal import Decimal
from datetime import datetime

class Command(BaseCommand):
    help = 'Adds sample revenue data for the last 12 months'

    def handle(self, *args, **kwargs):
        current_date = datetime.now()
        
        # Generate data for the last 12 months
        for i in range(12):
            # Calculate the date for this iteration
            if current_date.month - i <= 0:
                year = current_date.year - 1
                month = 12 + (current_date.month - i)
            else:
                year = current_date.year
                month = current_date.month - i

            # Generate random but realistic revenue data
            total_revenue = Decimal(str(round(1000000 + (i * 50000), 2)))  # Base revenue + monthly growth
            total_expenses = Decimal(str(round(total_revenue * Decimal('0.3'), 2)))  # 30% of revenue
            net_profit = total_revenue - total_expenses

            # Create or update the revenue record
            Revenue.objects.update_or_create(
                year=year,
                month=month,
                defaults={
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'net_profit': net_profit
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully added sample revenue data')) 