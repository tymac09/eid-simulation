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
