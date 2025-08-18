from django.contrib import admin
from .models import TaxYear, TaxBracket, ContributionRule

@admin.register(TaxYear)
class TaxYearAdmin(admin.ModelAdmin):
    list_display = ("year", "country")
    list_filter = ("country",)

@admin.register(TaxBracket)
class TaxBracketAdmin(admin.ModelAdmin):
    list_display = ("tax_year","lower","upper","rate")
    list_filter = ("tax_year",)

@admin.register(ContributionRule)
class ContributionRuleAdmin(admin.ModelAdmin):
    list_display = ("tax_year","name","rate","cap")
    list_filter = ("tax_year",)
