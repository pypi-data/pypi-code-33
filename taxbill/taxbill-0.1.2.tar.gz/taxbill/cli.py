# pylint: disable=missing-docstring, bad-continuation
from datetime import datetime
from pkgutil import get_data

import click
from yaml import load

from taxbill.calculator import all_taxes
from taxbill.optimiser import run

RATES = load(get_data("taxbill", "rates.yml").decode("utf8"))
CURRENT_YEAR = datetime.now().year


def display(
    salary,
    dividend,
    employer_pension,
    personal_pension,
    employers_ni=0,
    employees_ni=0,
    income_tax_earnings=0,
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

    print(f"Salary: £{salary}")
    print(f"Dividend: £{dividend}")
    print(f"Employer Pension Contribution: £{employer_pension}")
    print(f"Personal Pension Contribution: £{personal_pension}")
    print("------")
    print(f"Employer NI contribution: £{employers_ni}")
    print(f"Employee NI contribution: £{employees_ni}")
    print(f"Income Tax on Salary: £{income_tax_earnings}")
    print(f"Income Tax on Dividend: £{income_tax_dividend}")
    print(f"Tax Relief on Pension Contribution: £{income_tax_pension_relief}")
    print(f"Corporation Tax Saving: £{corporation_tax}")
    print("---")
    print(f"Total Withdrawn Gross: £{total_gross_drawings}")
    print(f"Total Personal Taxes: £{personal_tax}")
    print(f"Total Withdrawn Net: £{total_gross_drawings - personal_tax}\n")
    print(f"Total Corporate Taxes: £{corporate_tax}")
    print(f"Total Tax: £{total_tax}\n")
    print(f"Total Tax / Gross Withdrawn: {effective_tax_pct}%")


@click.version_option(prog_name="taxbill")
@click.group()
def taxbill():
    pass


@taxbill.command()
@click.option(
    "-s", "--salary", default=0, prompt="Salary", help="Annual gross salary"
)
@click.option(
    "-d",
    "--dividend",
    default=0,
    prompt="Dividend",
    help="Total dividend payments",
)
@click.option(
    "-e",
    "--employer_pension",
    default=0,
    prompt="Employer Pension Contribution",
    help="Total employer pension contributions",
)
@click.option(
    "-p",
    "--personal_pension",
    default=0,
    prompt="Personal Pension Contribution",
    help="Total personal pension contributions",
)
@click.option(
    "-y",
    "--year",
    type=int,
    default=CURRENT_YEAR,
    prompt="Tax year ending in",
    help="Calendar year in which tax year ends",
)
def calculate(salary, dividend, employer_pension, personal_pension, year):
    taxes = all_taxes(
        salary, dividend, personal_pension, employer_pension, RATES[year]
    )
    display(
        salary=salary,
        dividend=dividend,
        employer_pension=employer_pension,
        personal_pension=personal_pension,
        **taxes,
    )


@taxbill.command()
@click.option(
    "-r",
    "--requirement",
    type=int,
    prompt="Required amount",
    help="Total required withdrawals",
)
@click.option(
    "-p",
    "--pension",
    type=int,
    prompt="Pension Contribution",
    help="Total required pension contribution",
)
@click.option(
    "-y",
    "--year",
    type=int,
    default=CURRENT_YEAR,
    prompt="Tax year ending in",
    help="Calendar year in which tax year ends",
)
def optimise(requirement, pension, year):
    optimal = run(requirement=requirement, pension=pension, rates=RATES[year])
    taxes = all_taxes(rates=RATES[year], **optimal)
    display(**optimal, **taxes)
