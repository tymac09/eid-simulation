from django.core.management.base import BaseCommand
from decimal import Decimal
from taxes.models import TaxYear, TaxBracket, ContributionRule

class Command(BaseCommand):
    help = "Seed Vietnam 2025 demo rules (educational)."

    def handle(self, *args, **kwargs):
        ty, _ = TaxYear.objects.get_or_create(year=2025, country="VN")
        ty.brackets.all().delete(); ty.contrib_rules.all().delete()

        brackets = [
            (0,        60000000,   5),
            (60000000, 120000000, 10),
            (120000000,216000000, 15),
            (216000000,384000000, 20),
            (384000000,624000000, 25),
            (624000000,960000000, 30),
            (960000000,None,      35),
        ]
        for lower, upper, rate in brackets:
            TaxBracket.objects.create(
                tax_year=ty,
                lower=Decimal(lower),
                upper=Decimal(upper) if upper is not None else None,
                rate=Decimal(rate)
            )

        ContributionRule.objects.create(tax_year=ty, name="Social Security", rate=Decimal("8.0"),  cap=Decimal("29800000"))
        ContributionRule.objects.create(tax_year=ty, name="Health Insurance", rate=Decimal("1.5"), cap=Decimal("4470000"))

        self.stdout.write(self.style.SUCCESS("Seeded VN-2025 rules."))
