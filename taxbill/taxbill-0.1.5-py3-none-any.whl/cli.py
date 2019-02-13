# pylint: disable=missing-docstring, bad-continuation
from datetime import datetime
from pkgutil import get_data

import click
from yaml import load

from taxbill.calculator import all_taxes
from taxbill.optimiser import run
from taxbill.analyser import analyse

RATES = load(get_data("taxbill", "rates.yml").decode("utf8"))
CURRENT_YEAR = datetime.now().year


def display(results):
    for block, contents in results.items():
        for label, value in contents.items():
            if label != "Total Tax / Gross Withdrawn":
                print(f"{label}: £{value}")
            else:
                print(f"{label}: {value}%")
        print("")


@click.version_option(prog_name="taxbill")
@click.group()
def taxbill():
    pass


@taxbill.command()
@click.option("-s", "--salary", default=0, prompt="Salary", help="Annual gross salary")
@click.option(
    "-d", "--dividend", default=0, prompt="Dividend", help="Total dividend payments"
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
    taxes = all_taxes(salary, dividend, personal_pension, employer_pension, RATES[year])
    analysis = analyse(salary, dividend, employer_pension, personal_pension, **taxes)
    display(analysis)


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
    analysis = analyse(**optimal, **taxes)
    display(analysis)
