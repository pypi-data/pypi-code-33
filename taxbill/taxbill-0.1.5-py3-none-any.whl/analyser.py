# pylint: disable=missing-docstring, bad-continuation, too-many-arguments


def analyse(
    salary,
    dividend,
    employer_pension, personal_pension, employers_ni=0, employees_ni=0, income_tax_earnings=0,
    income_tax_dividend=0,
    income_tax_pension_relief=0,
    corporation_tax=0,
):

    total_gross_drawings = salary + dividend + employer_pension
    corporate_tax = round(employers_ni - corporation_tax, 2)
    personal_tax = round(
        income_tax_earnings
        + income_tax_dividend
        + employees_ni
        - income_tax_pension_relief,
        2,
    )
    total_tax = round(corporate_tax + personal_tax, 2)
    effective_tax_pct = round(total_tax * 100 / total_gross_drawings, 2)

    return {
        "input": {
            "Salary": salary,
            "Dividend": dividend,
            "Employer Pension Contribution": employer_pension,
            "Personal Pension Contribution": personal_pension,
        },
        "taxes": {
            "Employer NI contribution": employers_ni,
            "Employee NI contribution": employees_ni,
            "Income Tax on Salary": income_tax_earnings,
            "Income Tax on Dividend": income_tax_dividend,
            "Tax Relief on Pension Contribution": income_tax_pension_relief,
            "Corporation Tax Saving": corporation_tax,
        },
        "totals": {
            "Total Withdrawn Gross": total_gross_drawings,
            "Total Personal Taxes": personal_tax,
            "Total Withdrawn Net": total_gross_drawings - personal_tax,
            "Total Corporate Taxes": corporate_tax,
            "Total Tax": total_tax,
            "Total Tax / Gross Withdrawn": effective_tax_pct,
        },
    }
