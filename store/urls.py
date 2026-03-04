from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]