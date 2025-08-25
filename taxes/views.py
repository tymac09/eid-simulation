from rest_framework import permissions, views, status, viewsets, decorators, mixins
from rest_framework.response import Response

from .models import TaxYear, IncomeEntry, DeductionEntry, TaxReturn
from .serializers import (
    PreviewInputSerializer, PreviewOutputSerializer,
    IncomeEntrySerializer, DeductionEntrySerializer, TaxReturnSerializer,
)
from .services import compute_summary
from django.utils.timezone import localtime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .utils_pdf import render_to_pdf


class PreviewReturnView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = PreviewInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        year = s.validated_data["tax_year"]
        country = s.validated_data["country"]
        incomes = s.validated_data["incomes"]
        deductions = s.validated_data.get("deductions", [])

        try:
            ty = TaxYear.objects.prefetch_related("brackets", "contrib_rules").get(
                year=year, country=country
            )
        except TaxYear.DoesNotExist:
            return Response(
                {"detail": "Tax rules not found for that year/country."},
                status=status.HTTP_404_NOT_FOUND,
            )

        gross = sum(incomes) if incomes else 0
        ded = sum(deductions) if deductions else 0
        summary = compute_summary(gross, ded, ty.brackets.all(), ty.contrib_rules.all())

        out = PreviewOutputSerializer(summary)
        return Response(out.data, status=status.HTTP_200_OK)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IncomeEntryViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeEntrySerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return IncomeEntry.objects.filter(user=self.request.user).select_related("tax_year")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeductionEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DeductionEntrySerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return DeductionEntry.objects.filter(user=self.request.user).select_related("tax_year")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaxReturnViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = TaxReturnSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return TaxReturn.objects.filter(user=self.request.user).select_related("tax_year")

    @decorators.action(detail=False, methods=["post"], url_path="compute-submit")
    def compute_submit(self, request):
        """
        Body:
        {
          "tax_year": 2025,
          "country": "VN" | "US",
          "submit": true|false  (default false)
        }
        Computes from existing IncomeEntry/DeductionEntry for this user+year+country,
        returns summary; if submit=true, saves/updates TaxReturn.
        """
        year = int(request.data.get("tax_year"))
        country = request.data.get("country", "VN")
        submit = bool(request.data.get("submit", False))

        try:
            ty = TaxYear.objects.prefetch_related("brackets", "contrib_rules").get(
                year=year, country=country
            )
        except TaxYear.DoesNotExist:
            return Response(
                {"detail": "Tax rules not found for that year/country."},
                status=status.HTTP_404_NOT_FOUND,
            )

        incomes = IncomeEntry.objects.filter(user=request.user, tax_year=ty).values_list("amount", flat=True)
        deds = DeductionEntry.objects.filter(user=request.user, tax_year=ty).values_list("amount", flat=True)

        gross = sum(incomes) if incomes else 0
        ded = sum(deds) if deds else 0

        summary = compute_summary(gross, ded, ty.brackets.all(), ty.contrib_rules.all())

        if submit:
            tr, _ = TaxReturn.objects.get_or_create(
                user=request.user, tax_year=ty, defaults={"status": "draft"}
            )
            tr.gross_income = summary["gross_income"]
            tr.total_deductions = summary["total_deductions"]
            tr.taxable_income = summary["taxable_income"]
            tr.income_tax = summary["income_tax"]
            tr.contributions = summary["contributions"]
            tr.net_income = summary["net_income"]
            tr.status = "submitted"
            tr.save()

        return Response({**summary, "submitted": submit}, status=status.HTTP_200_OK)
    
class ReturnHTMLView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        tr = get_object_or_404(TaxReturn, pk=pk, user=request.user)
        incomes = IncomeEntry.objects.filter(user=request.user, tax_year=tr.tax_year)
        deductions = DeductionEntry.objects.filter(user=request.user, tax_year=tr.tax_year)
        ctx = {
            "return": tr,
            "user": request.user,
            "incomes": incomes,
            "deductions": deductions,
            "now": localtime(),
        }
        # Return regular HTML page (so you can open it via Swagger)
        return render(request, "taxes/return_detail.html", ctx)


class ReturnPDFView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        tr = get_object_or_404(TaxReturn, pk=pk, user=request.user)
        incomes = IncomeEntry.objects.filter(user=request.user, tax_year=tr.tax_year)
        deductions = DeductionEntry.objects.filter(user=request.user, tax_year=tr.tax_year)
        ctx = {
            "return": tr,
            "user": request.user,
            "incomes": incomes,
            "deductions": deductions,
            "now": localtime(),
        }
        pdf_bytes, err = render_to_pdf("taxes/return_pdf.html", ctx)
        if err or not pdf_bytes:
            return Response({"detail": "Failed to generate PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        filename = f"{tr.tax_year.country}-{tr.tax_year.year}-return-{tr.id}.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        resp["X-Content-Type-Options"] = "nosniff"
        return resp