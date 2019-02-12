from collections import defaultdict


def single_band_tax_amount(taxable_amount, rate, threshold=0):
    """Compute the taxable amount for a single band of tax.

    e.g. Income tax is split into basic and higher bands. This will compute
    the amount for either one of those if passed the threshold and rate for that
    band.
    """
    if taxable_amount < threshold:
        return 0

    return rate * (taxable_amount - threshold)


def tax_amount(taxable_amount, bands):
    """Compute the total amount for a tax.

    This will compute the amount for each band a tax and return the sum of
    those amounts. e.g For income tax, it will return the sum of both the basic
    and higher band amounts.
    """
    amounts = [
        single_band_tax_amount(
            min([taxable_amount, band["limit"]]), band["rate"], band["threshold"]
        )
        for band in bands
    ]
    return round(sum(amounts), 2)


def salary_taxes(salary, rates):
    """NI and income tax on earnings are banded taxes based on the salary
    amount. We can use a comprehension to loop over those taxes and
    compute relevant amounts.
    """
    return {
        tax: tax_amount(salary, rates[tax])
        for tax in ["employees_ni", "employers_ni", "income_tax_earnings"]
    }


def dividend_tax(salary, dividend, rates):
    """Dividend tax uses the income tax earnings bands to determine the
    appropriate rate.
    """
    # Work out which income tax band applies to the sum of salary and
    # dividend amounts.
    idx, _ = next(
        (idx, band)
        for idx, band in enumerate(rates["income_tax_earnings"])
        if band["limit"] > salary + dividend >= band["threshold"]
    )
    # Use that band to apply the relevant rate to the dividend amount
    rate = rates["income_tax_dividend"]["rates"][idx]
    threshold = rates["income_tax_dividend"]["threshold"]
    return single_band_tax_amount(dividend, rate, threshold)


def all_taxes(salary, dividend, personal_pension, employer_pension, rates):
    result = defaultdict(int)

    if salary:
        result.update(salary_taxes(salary, rates))

    if dividend:
        result["income_tax_dividend"] = dividend_tax(salary, dividend, rates)

    if personal_pension:
        result["income_tax_pension_relief"] = round(
            personal_pension * rates["income_tax_earnings"][1]["rate"], 2
        )

    corporation_tax = single_band_tax_amount(
        salary + result["employers_ni"] + employer_pension, rates["corporation_tax"]
    )
    result["corporation_tax"] = round(corporation_tax, 2)

    return result
