from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection
from django.db.models import Count, Avg, Min, Max
from .models import RFMScore
from .serializers import RFMScoreSerializer, RFMScoreListSerializer
from .queries import get_rfm_calculation_query
from customer.models import Customer


class RFMScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for RFM Scores.
    
    Provides read-only access to RFM scores.
    Use the 'calculate' action to recalculate RFM scores for all customers.
    """
    
    queryset = RFMScore.objects.select_related('customer').all()
    serializer_class = RFMScoreSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RFMScoreListSerializer
        return RFMScoreSerializer
    
    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        """
        Calculate RFM scores for all customers using SQL query.
        
        This endpoint executes the RFM calculation SQL query and
        creates/updates RFMScore records for all customers.
        """
        try:
            with connection.cursor() as cursor:
                # Execute the RFM calculation query
                cursor.execute(get_rfm_calculation_query())
                results = cursor.fetchall()
                
                # Column names from the query
                columns = [
                    'customer_id', 'recency_days', 'frequency', 'monetary',
                    'recency_score', 'frequency_score', 'monetary_score', 'segment'
                ]
                
                # Process results and create/update RFMScore records
                created_count = 0
                updated_count = 0
                
                for row in results:
                    row_dict = dict(zip(columns, row))
                    customer_id = row_dict['customer_id']
                    
                    try:
                        customer = Customer.objects.get(id=customer_id)
                    except Customer.DoesNotExist:
                        continue
                    
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
                    else:
                        updated_count += 1
                
                return Response({
                    'message': 'RFM scores calculated successfully',
                    'total_customers': len(results),
                    'created': created_count,
                    'updated': updated_count
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Failed to calculate RFM scores',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='by-segment')
    def by_segment(self, request):
        """
        Get RFM scores grouped by segment.
        
        Returns a summary of customers per segment.
        """
        segments = RFMScore.objects.values('segment').annotate(
            count=Count('customer_id')
        ).order_by('-count')
        
        return Response({
            'segments': list(segments),
            'total_customers': RFMScore.objects.count()
        })
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get RFM statistics.
        
        Returns aggregate statistics about RFM scores.
        """
        stats = RFMScore.objects.aggregate(
            total_customers=Count('customer_id'),
            avg_recency_days=Avg('recency_days'),
            avg_frequency=Avg('frequency'),
            avg_monetary=Avg('monetary'),
            min_recency_days=Min('recency_days'),
            max_recency_days=Max('recency_days'),
            min_frequency=Min('frequency'),
            max_frequency=Max('frequency'),
            min_monetary=Min('monetary'),
            max_monetary=Max('monetary'),
        )
        
        return Response(stats)
