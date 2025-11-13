"""
Health check view for Kubernetes liveness and readiness probes.
"""
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError


def health_check(request):
    """
    Health check endpoint for Kubernetes probes.
    Returns 200 if the application is healthy, 503 otherwise.
    """
    try:
        # Check database connection
        connection.ensure_connection()
        connection.cursor()
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'crm-api'
        }, status=200)
    except OperationalError:
        # Database connection failed
        return JsonResponse({
            'status': 'unhealthy',
            'service': 'crm-api',
            'error': 'database_connection_failed'
        }, status=503)
    except Exception as e:
        # Other errors
        return JsonResponse({
            'status': 'unhealthy',
            'service': 'crm-api',
            'error': str(e)
        }, status=503)

