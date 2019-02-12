from pulp import LpInteger, LpMinimize, LpProblem, LpStatus, LpVariable, lpSum


def run(requirement, pension, rates, income_tax_band=1):
    tax_band = rates["income_tax_earnings"][income_tax_band]
    employees_ni_band = rates["employees_ni"][income_tax_band]
    employers_ni_band = rates["employers_ni"][income_tax_band]
    dividend_threshold = rates["income_tax_dividend"]["threshold"]
    dividend_rate = rates["income_tax_dividend"]["rates"][income_tax_band]

    problem = LpProblem(name="Optimise Tax", sense=LpMinimize)

    salary = LpVariable(
        name="salary",
        lowBound=tax_band["threshold"],
        upBound=tax_band["limit"],
        cat=LpInteger,
    )
    dividend = LpVariable(
        name="dividend", lowBound=0, upBound=tax_band["limit"], cat=LpInteger
    )
    personal_pension = LpVariable(
        name="personal_pension", lowBound=0, upBound=tax_band["limit"], cat=LpInteger
    )
    employer_pension = LpVariable(
        name="employer_pension", lowBound=0, upBound=tax_band["limit"], cat=LpInteger
    )

    problem += (
        # Employees NI contribution
        employees_ni_band["rate"] * (salary - employees_ni_band["threshold"])
        # Employers NI contribution
        + employers_ni_band["rate"] * (salary - employers_ni_band["threshold"])
        # Corporation tax saving on employers NI contribution
        - rates["corporation_tax"]
        * employers_ni_band["rate"]
        * (salary - employers_ni_band["threshold"])
        # Income tax on salary
        + tax_band["rate"] * (salary - tax_band["threshold"])
        # Income tax on dividend
        + dividend_rate * (dividend - dividend_threshold)
        # Corporation tax saving on salary
        - rates["corporation_tax"] * salary
        # Income tax relief on personal pension contribution
        - tax_band["rate"] * personal_pension
        # Corporation Tax saving on employer pension contribution
        - rates["corporation_tax"] * employer_pension,
        "TotalTaxBill",
    )

    problem += (salary + dividend + employer_pension == requirement, "RequiredAmount")
    problem += personal_pension <= salary, "PensionLimitation"
    problem += (employer_pension + personal_pension == pension, "PensionRequirement")

    problem.solve()

    if LpStatus[problem.status] != "Optimal":
        raise ValueError("No solution found")

    return {v.name: v.varValue for v in problem.variables()}
