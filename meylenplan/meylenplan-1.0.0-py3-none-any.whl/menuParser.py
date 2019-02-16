import datetime
import subprocess

def parse_menu(text_file):
    lines = read_file(text_file)
    meal_list = find_meal_names(lines)
    meal_week_map = sort_meals_by_day(meal_list)
    weekday = get_weekday()
    meals = get_todays_meals(meal_week_map, weekday)

    return meals

def find_meal_names(lines):
    meal_names = []

    for line in lines:
        if len(line) >= 25:
            meal_names.append(line)

    # cut off ingredient infos
    meal_names = meal_names[:-2]

    return (meal_names)


def sort_meals_by_day(meal_names):

    meals = {'monday': meal_names[0:5],
             'tuesday': meal_names[5:10],
             'wednesday': meal_names[10:15],
             'thursday': meal_names[15:20],
             'friday': meal_names[20:25],
             'saturday': None,
             'sunday': None
             }

    return meals


def get_weekday():
    weekdays = {0: 'monday',
                1: 'tuesday',
                2: 'wednesday',
                3: 'thursday',
                4: 'friday',
                5: 'saturday',
                6: 'sunday'}

    return weekdays[datetime.datetime.today().weekday()]


def get_todays_meals(meal_map, day):
    if meal_map[day] is not None:
        meals = []
        for meal in meal_map[day]:
            meals.append(meal)
        return meals
    else:
        return None


def read_file(file_name):

    with open(file_name) as file:
        lines = file.readlines()

    # remove whitespace characters like `\n` at the end of each line
    lines = [line.strip() for line in lines]
    # remove empty lines
    lines = [line for line in lines if line]

    return lines
