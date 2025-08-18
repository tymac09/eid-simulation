from rest_framework import permissions, views, response, status
from .models import TaxYear
from .serializers import PreviewInputSerializer, PreviewOutputSerializer
from .services import compute_summary

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
            ty = TaxYear.objects.prefetch_related("brackets","contrib_rules").get(year=year, country=country)
        except TaxYear.DoesNotExist:
            return response.Response({"detail":"Tax rules not found for that year/country."}, status=status.HTTP_404_NOT_FOUND)

        gross = sum(incomes) if incomes else 0
        ded = sum(deductions) if deductions else 0
        summary = compute_summary(gross, ded, ty.brackets.all(), ty.contrib_rules.all())

        out = PreviewOutputSerializer(summary)
        return response.Response(out.data, status=status.HTTP_200_OK)
