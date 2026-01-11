"""
Management command to calculate RFM scores for all customers.

Usage:
    python manage.py calculate_rfm
    python manage.py calculate_rfm --verbose
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Count
from django.utils import timezone
from customer.models import Customer
from rfm.models import RFMScore
from rfm.queries import get_rfm_calculation_query


class Command(BaseCommand):
    help = 'Calculate RFM (Recency, Frequency, Monetary) scores for all customers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be calculated without saving',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        dry_run = options['dry_run']
        
        if verbose:
            self.stdout.write('Starting RFM calculation...')
        
        try:
            with connection.cursor() as cursor:
                # Execute the RFM calculation query
                if verbose:
                    self.stdout.write('Executing RFM calculation SQL query...')
                
                cursor.execute(get_rfm_calculation_query())
                results = cursor.fetchall()
                
                # Column names from the query
                columns = [
                    'customer_id', 'recency_days', 'frequency', 'monetary',
                    'recency_score', 'frequency_score', 'monetary_score', 'segment'
                ]
                
                if verbose:
                    self.stdout.write(f'Found {len(results)} customers to process')
                
                # Process results and create/update RFMScore records
                created_count = 0
                updated_count = 0
                skipped_count = 0
                
                for row in results:
                    row_dict = dict(zip(columns, row))
                    customer_id = row_dict['customer_id']
                    
                    try:
                        customer = Customer.objects.get(id=customer_id)
                    except Customer.DoesNotExist:
                        skipped_count += 1
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(f'Customer {customer_id} not found, skipping...')
                            )
                        continue
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would calculate RFM for {customer.name}: '
                            f'R={row_dict["recency_score"]} '
                            f'F={row_dict["frequency_score"]} '
                            f'M={row_dict["monetary_score"]} '
                            f'-> {row_dict["segment"]}'
                        )
                    else:
                        # Create or update RFMScore
                        rfm_score, created = RFMScore.objects.update_or_create(
                            customer=customer,
                            defaults={
                                'recency_days': row_dict['recency_days'],
                                'frequency': row_dict['frequency'],
                                'monetary': row_dict['monetary'],
                                'recency_score': row_dict['recency_score'],
                                'frequency_score': row_dict['frequency_score'],
                                'monetary_score': row_dict['monetary_score'],
                                'segment': row_dict['segment'],
                            }
                        )
                        
                        if created:
                            created_count += 1
                            if verbose:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'Created RFM score for {customer.name}: {rfm_score.segment}'
                                    )
                                )
                        else:
                            updated_count += 1
                            if verbose:
                                self.stdout.write(
                                    f'Updated RFM score for {customer.name}: {rfm_score.segment}'
                                )
                
                # Summary
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f'\nDRY RUN: Would process {len(results)} customers '
                            f'(skipped: {skipped_count})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\nRFM calculation completed successfully!'
                        )
                    )
                    self.stdout.write(
                        f'Total customers processed: {len(results)}'
                    )
                    self.stdout.write(
                        f'Created: {created_count} | Updated: {updated_count} | Skipped: {skipped_count}'
                    )
                    
                    # Show segment distribution
                    if verbose:
                        self.stdout.write('\nSegment distribution:')
                        from django.db.models import Count
                        segments = RFMScore.objects.values('segment').annotate(
                            count=Count('customer_id')
                        ).order_by('-count')
                        for seg in segments:
                            self.stdout.write(f'  {seg["segment"]}: {seg["count"]}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error calculating RFM scores: {str(e)}')
            )
            if verbose:
                import traceback
                self.stdout.write(traceback.format_exc())
            raise
