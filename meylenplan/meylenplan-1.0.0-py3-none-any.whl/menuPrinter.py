from tabulate import tabulate

def print_menu(meals):
    if meals is not None:
        table = []
        for meal in meals:
            table.append([meal, "Null"])
        print(tabulate(table, headers=['Essen', 'Preis'], tablefmt='orgtbl'))
    else:
        print("Ich habe heute leider kein Essen für dich.")
