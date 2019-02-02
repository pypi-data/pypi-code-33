import sqlite3
import sys

from muscle.model.model import Exercise
from muscle.util.errors import RoutineNotFoundError, DatabaseNotFoundError, \
    RecordAlreadyEnteredError, DuplicateExerciseError, \
    DuplicateRoutineNameError
from muscle.util.format import num_to_ordinal


def show_history(controller):
    workout_history = controller.workout_history()
    if controller.workout_history_is_empty():
        print("There is no workout history.")
        return
    for date, rout_ex in workout_history.items():
        print(date + ": ", end="")
        for ex in rout_ex[1:]:
            print(ex.name + "(" + ex.rep + ")" + str(ex.weight), end=" ")


def record(controller):
    list_routine(controller)
    routine_name = input("Enter the routine you did today: ")
    try:
        exercise_list = controller.list_exercises(routine_name)
    except RoutineNotFoundError:
        exit(controller, "ERROR: The routine entered is not valid")
    today_exercises = []
    for exercise in exercise_list:
        weight = input("Enter the weight of " + exercise.name + ": ")
        if not weight.isdigit() or int(weight) <= 0:
            exit(controller, "ERROR: You must enter a positive integer")
        today_exercises.append(Exercise(exercise.name, exercise.rep, weight))
    try:
        controller.record(today_exercises, routine_name)
    except RecordAlreadyEnteredError:
        exit(controller, "ERROR: you already entered this routine for today")


def delete_record(controller, date=None):
    if controller.workout_history_is_empty():
        exit(controller, "ERROR: workout history is empty")
    if date is None:
        date = controller.last_record_date()
    try:
        controller.delete_record(date)
    except KeyError:
        exit(controller, "ERROR: date not valid")
    print("workout record on " + date + " has been deleted")


def list_routine(controller):
    if controller.routine_list_is_empty():
        exit(controller, "You don't have any routine stored")
    print("Available routines:")
    routine_list = controller.list_routines()
    for routine in routine_list:
        print(routine.name + ": ", end="")
        for ex in routine.exercise_list:
            if routine.exercise_list[0] is not ex:
                print(" " * (len(routine.name) + 2), end="")
            print(ex.name + "(" + ex.rep + ")")
        print()


def add_routine(controller):
    routine_name = input("Enter the name of the routine: ")
    num_exercises = input("How many exercises does the routine have? ")
    if not num_exercises.isdigit() or int(num_exercises) <= 0:
        exit(controller, "ERROR: You must enter a positive integer")
    exercise_list = []
    for i in range(1, int(num_exercises) + 1):
        ordinal = num_to_ordinal(i)
        exercise_name = input("Name of the " + ordinal + " exercise: ")
        exercise_rep = input("Repetition of the " + ordinal + " exercise: ")
        exercise_list.append(Exercise(exercise_name, exercise_rep))
    try:
        controller.add_routine(routine_name, exercise_list)
    except DuplicateRoutineNameError:
        exit(controller, "ERROR: Duplicate routine name.")
    except DuplicateExerciseError:
        exit(controller, "ERROR: Duplicate exercise name.")


def delete_routine(controller, routine_name=None):
    if routine_name is None:
        list_routine(controller)
        routine_name = input("Enter the name of the routine: ")

    try:
        controller.delete_routine(routine_name)
    except RoutineNotFoundError:
        exit(controller, "ERROR: The routine entered is not valid")


def import_db(controller, path):
    try:
        controller.import_db(path)
    except DatabaseNotFoundError:
        sys.exit("ERROR: database does not exist")
    except sqlite3.Error:
        sys.exit("ERROR: database is not valid")
    else:
        print("database imported from " + path)
    finally:
        controller.terminate()


def export_db(controller, path):
    controller.export_db(path)
    print("database exported to " + path)


def gui(controller):
    print("GUI not implemented yet")


def exit(controller, error_message):
    controller.terminate()
    sys.exit(error_message)
