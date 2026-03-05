from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, InvoiceViewSet, generate_invoice_pdf

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("invoices/<int:pk>/pdf/", generate_invoice_pdf),
]