from .models import IncomeEntry, DeductionEntry, TaxReturn, TaxYear
from django.contrib.auth.models import User
from rest_framework import serializers


class PreviewInputSerializer(serializers.Serializer):
    tax_year = serializers.IntegerField()
    country = serializers.ChoiceField(choices=[("VN","VN"),("US","US")], default="VN")
    incomes = serializers.ListField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    deductions = serializers.ListField(child=serializers.DecimalField(max_digits=12, decimal_places=2), required=False)

class PreviewOutputSerializer(serializers.Serializer):
    gross_income = serializers.CharField()
    total_deductions = serializers.CharField()
    taxable_income = serializers.CharField()
    income_tax = serializers.CharField()
    contributions = serializers.CharField()
    net_income = serializers.CharField()

class IncomeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeEntry
        fields = ("id", "source", "amount", "tax_year")

class DeductionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeductionEntry
        fields = ("id", "label", "amount", "tax_year")

class TaxReturnSerializer(serializers.ModelSerializer):
    tax_year = serializers.PrimaryKeyRelatedField(queryset=TaxYear.objects.all())
    class Meta:
        model = TaxReturn
        fields = ("id","tax_year","status","gross_income","total_deductions","taxable_income","income_tax","contributions","net_income","created_at","updated_at")
        read_only_fields = ("gross_income","total_deductions","taxable_income","income_tax","contributions","net_income","created_at","updated_at")