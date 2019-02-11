import json
import os
import copy
from pkg_resources import Requirement, resource_filename

from keys import *

def monthly():
    budget_file_name = resource_filename(Requirement.parse("tdbudget"), os.path.join("tdbudget", "budget.json"))

    # Load up the budget
    budget = None
    with open(budget_file_name, "r") as budget_file:
        budget = json.load(budget_file)

    # Reset each bucket and remember the old amount
    old_budget = copy.deepcopy(budget)
    for bucket in budget[MONTHLY]:
        bucket[SAVED] = 0

    # Write out this month's savings
    with open(os.path.join(os.path.expanduser("~"), ".tdbudget", "log.json"), "w") as f:
        json.dump(old_budget, f, indent=4, sort_keys=True)

    # Write out the buckets with the savings cleared to 0
    with open(budget_file_name, "w") as f:
        json.dump(budget, f, indent=4, sort_keys=True)
        
    print(budget)

if __name__ == "__main__":
    monthly()
