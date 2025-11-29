"""
Custom middleware for Kubernetes health checks.
This middleware bypasses ALLOWED_HOSTS validation for health check endpoints.
"""
from django.utils.deprecation import MiddlewareMixin


class KubernetesHealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware that bypasses ALLOWED_HOSTS validation for health check endpoints.
    This allows Kubernetes health probes to work even if the Host header doesn't match ALLOWED_HOSTS.
    Must be placed before CommonMiddleware in MIDDLEWARE list.
    """
    
    def process_request(self, request):
        # Check if this is a health check request
        if request.path == '/health':
            # For health checks, set a flag to bypass ALLOWED_HOSTS check
            # We'll handle this in process_response by catching the exception
            request._health_check = True
            # Also modify Host header to localhost to help with validation
            original_host = request.META.get('HTTP_HOST', '')
            request.META['HTTP_HOST'] = 'localhost'
            request._original_host = original_host
        return None
    
    def process_response(self, request, response):
        # Restore original host if it was modified
        if hasattr(request, '_original_host'):
            request.META['HTTP_HOST'] = request._original_host
        return response

