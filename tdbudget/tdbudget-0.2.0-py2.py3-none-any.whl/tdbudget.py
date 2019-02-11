import click
import json
import os
import subprocess
import sys
from pkg_resources import Requirement, resource_filename

from .keys import *

def category_defn(budget, category_name):
    is_monthly = [category for category in budget[MONTHLY] if category[CATEGORY_NAME] == category_name]
    is_long_term = [category for category in budget[LONG_TERM] if category[CATEGORY_NAME] == category_name]

    if is_monthly:
        assert len(is_monthly) is 1
        assert len(is_long_term) is 0
        return is_monthly[0]
    elif is_long_term:
        assert len(is_long_term) is 1
        assert len(is_monthly) is 0
        return is_long_term[0]
    else:
        return None

def get_budget():
    # Load the current budget data
    budget_path = resource_filename(Requirement.parse("tdbudget"), os.path.join("tdbudget", "budget.json"))
    budget_file = open(budget_path, "r")
    budget = json.load(budget_file)
    budget_file.close()

    return budget

def write_budget(new_budget):
    budget_path = resource_filename(Requirement.parse("tdbudget"), os.path.join("tdbudget", "budget.json"))
    with open(budget_path, "w") as budget_file:
        json.dump(new_budget, budget_file, indent=4, sort_keys=True)

        
@click.group()
def cli():
    pass


@cli.command()
@click.argument('category')
@click.argument('amount')
def spend(category, amount):
    budget = get_budget()

    # Get the block corresponding to this category and add the new $
    defn = category_defn(budget, category)
    defn[SAVED] += float(amount)

    budget["slush"] -= float(amount)
    if not budget["slush"] < 0:
        print("Whoa there. You've spent more money than you brought in. Just letting you know.")
    
    write_budget(budget)

cli.add_command(spend)


@cli.command()
@click.argument('amount')
def add(amount):
    budget = get_budget()
    budget["slush"] += float(amount)
    write_budget(budget)

cli.add_command(add)


@cli.command()
@click.argument('category')
def check(category):
    budget = get_budget()
    if category == SLUSH:
        print(budget[SLUSH])
        return
    
    print(category_defn(budget, category))
    


@cli.command()
def init():
    # Make the budget where generated reports will go (~/.tdbudget)
    home = os.path.expanduser("~")
    if home.endswith('/'):
        home = home[:-1]
        
    try:
        os.mkdir(os.path.join(home, ".tdbudget"))
    except:
        "setup had problems making the directory " + os.path.join(home, ".tdbudget")
        pass

    # Check that the user is ok with us installing a cronjob
    val = None
    while val != "y" and val != "n":
        val = input("tdbudget will install a cronjob to reset monthly savings targets and generate a report. installation will continue if you don't want this, but functionality will be far more manual + limited. Do you want to install the cronjob? [y/n]: ")

    # Install the cronjob
    if val == "y":
        day = input("What day of the month do you want to use as a delimiter? Please enter a single number between 1 and 28. You can change this later with \'tdbudget conf month_start X\': ")
        conf_file_path = resource_filename(Requirement.parse("tdbudget"), os.path.join("tdbudget", "conf.json"))
        conf_file = json.load(open(conf_file_path, "r"))
        conf_file[MONTH_START] = int(day)
            
        monthly_path = resource_filename(Requirement.parse("tdbudget"), os.path.join("tdbudget", "monthly.bat"))
        script = 'schtasks.exe /create /tn \"tdbudget_monthly\" /tr \"{} {}\" /st 19:03 /sc MONTHLY /D {}'\
                     .format(sys.executable,\
                         resource_filename(Requirement.parse("tdbudget"), os.path.join("tdbudget", "monthly.py")),\
                         day)
        print(script)

        subprocess.run(script)

cli.add_command(init)

def main():
    cli()

if __name__ == "__main__":
    cli()

        
