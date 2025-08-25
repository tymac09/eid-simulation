from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreviewReturnView, IncomeEntryViewSet, DeductionEntryViewSet, TaxReturnViewSet, ReturnHTMLView, ReturnPDFView

router = DefaultRouter()
router.register(r'incomes', IncomeEntryViewSet, basename='income')
router.register(r'deductions', DeductionEntryViewSet, basename='deduction')
router.register(r'returns', TaxReturnViewSet, basename='return')

urlpatterns = [
    path("returns/preview/", PreviewReturnView.as_view(), name="returns-preview"),
    path("", include(router.urls)),
    path("returns/<int:pk>/view/", ReturnHTMLView.as_view(), name="return-html"),
    path("returns/<int:pk>/pdf/", ReturnPDFView.as_view(), name="return-pdf"),

]
