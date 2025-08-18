from django.core.management.base import BaseCommand
from decimal import Decimal
from taxes.models import TaxYear, TaxBracket, ContributionRule

class Command(BaseCommand):
    help = "Seed US 2025 demo rules (federal single; employee FICA). Educational only."

    def handle(self, *args, **kwargs):
        ty, _ = TaxYear.objects.get_or_create(year=2025, country="US")
        ty.brackets.all().delete(); ty.contrib_rules.all().delete()

        brackets = [
            (0,      12750,   10),
            (12750,  50250,   12),
            (50250,  95375,   22),
            (95375,  182100,  24),
            (182100, 231250,  32),
            (231250, 609350,  35),
            (609350, None,    37),
        ]
        for lower, upper, rate in brackets:
            TaxBracket.objects.create(
                tax_year=ty,
                lower=Decimal(lower),
                upper=Decimal(upper) if upper is not None else None,
                rate=Decimal(rate)
            )

        ContributionRule.objects.create(
            tax_year=ty, name="Social Security (employee)", rate=Decimal("6.2"),
            cap=Decimal("168600")
        )
        ContributionRule.objects.create(
            tax_year=ty, name="Medicare (employee)", rate=Decimal("1.45"),
            cap=None
        )

        self.stdout.write(self.style.SUCCESS("Seeded US-2025 rules."))
