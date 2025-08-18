from decimal import Decimal, ROUND_HALF_UP

def _money(x): return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calc_progressive_tax(taxable, brackets):
    tax = Decimal("0")
    remaining = Decimal(taxable)
    last_upper = Decimal("0")
    for b in brackets:
        upper = b.upper if b.upper is not None else None
        span = (upper - last_upper) if upper is not None else remaining
        if remaining <= 0: break
        chunk = min(remaining, span) if upper is not None else remaining
        tax += chunk * Decimal(b.rate) / Decimal("100")
        remaining -= chunk
        last_upper = upper or last_upper
    return _money(tax)

def calc_contributions(gross, rules):
    total = Decimal("0")
    gross = Decimal(gross)
    for r in rules:
        base = gross if r.cap is None else min(gross, r.cap)
        total += base * Decimal(r.rate) / Decimal("100")
    return _money(total)

def compute_summary(gross_income, deductions, brackets, contrib_rules):
    gross = _money(gross_income)
    ded = _money(deductions)
    taxable = _money(max(Decimal("0"), gross - ded))
    income_tax = calc_progressive_tax(taxable, brackets)
    contribs = calc_contributions(gross, contrib_rules)
    net = _money(gross - income_tax - contribs)
    return {
        "gross_income": str(gross),
        "total_deductions": str(ded),
        "taxable_income": str(taxable),
        "income_tax": str(income_tax),
        "contributions": str(contribs),
        "net_income": str(net),
    }
