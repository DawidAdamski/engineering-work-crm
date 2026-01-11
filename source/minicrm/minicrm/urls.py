"""
URL configuration for minicrm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os
from rest_framework.routers import DefaultRouter
from customer.views import CustomerViewSet
from order.views import OrderViewSet
from product.views import ProductViewSet
from rfm.views import RFMScoreViewSet
from .health import health_check

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'products', ProductViewSet)
router.register(r'rfm', RFMScoreViewSet, basename='rfm')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('health/', health_check, name='health'),
    path('health', health_check, name='health-no-slash'),  # Support both with and without trailing slash
]

# Serve static files in development/production (for DRF browsable API CSS)
# In production, consider using nginx or a CDN for better performance
if settings.DEBUG or os.environ.get('SERVE_STATIC', 'False').lower() == 'true':
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
