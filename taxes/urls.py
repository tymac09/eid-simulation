from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreviewReturnView, IncomeEntryViewSet, DeductionEntryViewSet, TaxReturnViewSet

router = DefaultRouter()
router.register(r'incomes', IncomeEntryViewSet, basename='income')
router.register(r'deductions', DeductionEntryViewSet, basename='deduction')
router.register(r'returns', TaxReturnViewSet, basename='return')

urlpatterns = [
    path("returns/preview/", PreviewReturnView.as_view(), name="returns-preview"),
    path("", include(router.urls)),
]
