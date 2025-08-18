from django.db import models
from django.contrib.auth.models import User

class TaxYear(models.Model):
    year = models.PositiveIntegerField()
    country = models.CharField(max_length=2, default="VN")  # 'VN' or 'US'

    class Meta:
        unique_together = ("year", "country")

    def __str__(self):
        return f"{self.country}-{self.year}"

class TaxBracket(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name="brackets")
    lower = models.DecimalField(max_digits=12, decimal_places=2)
    upper = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # None = no cap
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # percent
    class Meta:
        ordering = ["lower"]
    def __str__(self): return f"{self.tax_year}: {self.lower}-{self.upper or '∞'} @ {self.rate}%"

class ContributionRule(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name="contrib_rules")
    name = models.CharField(max_length=64)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    cap = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # None = no cap
    def __str__(self): return f"{self.tax_year} {self.name} {self.rate}%"

class IncomeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="income_entries")
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    source = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class DeductionEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deduction_entries")
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    label = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class TaxReturn(models.Model):
    STATUS_CHOICES = [("draft","Draft"),("submitted","Submitted")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tax_returns")
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft")
    gross_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contributions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ("user","tax_year")
