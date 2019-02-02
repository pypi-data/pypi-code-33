from muscle.util.database import Database
from muscle.util.errors import RoutineNotFoundError


def same_ex_list(history_ex_list, exercise_list):
    """
    Check if two exercise lists have the same exercises.

    They are the same if they have same exercises(name,rep) in the same order.
    :param history_ex_list: an exercise list from workout_history, weight!=None
    :param exercise_list: an exercise_list in a routine, weight=None
    :return: True if two exercise lists are the same, False otherwise
    """
    if len(history_ex_list) != len(exercise_list):
        return False
    for i in range(len(history_ex_list)):
        if history_ex_list[i].name != exercise_list[i].name:
            return False
        if history_ex_list[i].rep != exercise_list[i].rep:
            return False
    return True


class Model:
    """
    The model class of muscle.

    This class initializes a model from database, it also provides methods to
    update database.
    A model contains a list of user created routines and workout records.
    """

    def __init__(self, path):
        """
        Initialize a model.

        :param path: a PathLike object
        """
        self.db = Database(path)
        self.routine_list = self.init_routine_list()
        self.workout_history = self.init_workout_history()

    def init_routine_list(self):
        """
        Initialize a list of stored routines from the database.

        :return: a list of routine objects
        """
        routine_list = []
        routine_names = self.db.list_routines()
        for routine_name in routine_names:
            exercise_list = self.db.list_exercises(routine_name)
            exercise_list = [Exercise(*ex) for ex in exercise_list]
            routine_list.append(Routine(routine_name, exercise_list))
        return routine_list

    def init_workout_history(self):
        """
        Initialize a dict of workout history from the database.

        :return: a dict in this format {date: [routine_name, exercise...]}
        """
        workout_history = {}
        records = self.db.workout_record()
        for record in records:
            date = record[0]
            exercise = self.db.exercise(record[1])
            if record[2] is None:
                routine_name = 'deleted'
            else:
                routine_name = self.db.routine_name(record[2])[0]
            weight = record[3]
            exercise = Exercise(*exercise, weight)
            if date in workout_history.keys():
                workout_history[date].append(exercise)
            else:
                workout_history[date] = [routine_name, exercise]
        return workout_history

    def add_routine(self, routine):
        """
        Add a new routine, update both routine_list and database

        :param routine: a Routine object that contains a list of exercises
        :raises DuplicateRoutineNameError: if there's duplicate routine name
        :raises DuplicateExerciseError: if there's duplicate exercise
        """
        self.db.insert_routine(routine.name)
        routine_id = self.db.routine_id(routine.name)
        self.routine_list.append(routine)
        for exercise in routine.exercise_list:
            self.db.insert_exercise(exercise.name, exercise.rep)
            exercise_id = self.db.exercise_id(exercise.name, exercise.rep)
            self.db.insert_exercise_routine(exercise_id, routine_id)

        for date, rout_ex in self.workout_history.items():
            history_ex_list = rout_ex[1:]
            if same_ex_list(history_ex_list, routine.exercise_list):
                rout_ex[0] = routine.name
                self.db.update_routine_id_in_workout_record(date, routine_id)

    def list_exercises(self, routine_name):
        """
        Return a list of exercises given a routine_name.

        :param routine_name: the routine_name to list exercises
        :raises RoutineNotFoundError: if the routine_name doesn't exist
        """
        self.check_routine_name_exists(routine_name)
        for routine in self.routine_list:
            if routine.name == routine_name:
                return routine.exercise_list

    def record(self, date, exercise, routine_name):
        """
        Update workout_record table.

        :param date: today's date
        :param exercise: exercise to be recorded, weight can't be None
        :param routine_name: the workout routine to be recorded
        """
        exercise_id = self.db.exercise_id(exercise.name, exercise.rep)
        routine_id = self.db.routine_id(routine_name)
        weight = exercise.weight
        self.db.insert_workout_record(date, exercise_id, routine_id, weight)
        if date not in self.workout_history.keys():
            self.workout_history[date] = [routine_name, exercise]
        else:
            self.workout_history[date].append(exercise)

    def delete_routine(self, routine_name):
        """
        Delete a routine.

        :param routine_name: name of the routine to be deleted
        :raises RoutineNotFoundError: if the routine_name doesn't exist
        """
        self.check_routine_name_exists(routine_name)

        for routine in self.routine_list[:]:
            if routine.name == routine_name:
                self.routine_list.remove(routine)

        self.db.del_routine_from_ex_rout(routine_name)
        self.db.mark_routine_deleted(routine_name)
        self.db.del_from_routine_table(routine_name)

        for date, rout_ex in self.workout_history.items():
            if rout_ex[0] == routine_name:
                self.workout_history[date][0] = 'deleted'

    def delete_record(self, date):
        del self.workout_history[date]
        self.db.del_from_workout_record(date)

    def last_record_date(self):
        return self.db.last_record_date()

    def check_routine_name_exists(self, routine_name):
        """
        Check if the routine_name exists

        :param routine_name: the routine_name to check
        :raises RoutineNotFoundError: if the routine_name doesn't exist
        """
        if routine_name not in [routine.name for routine in self.routine_list]:
            raise RoutineNotFoundError

    def close_database_connection(self):
        self.db.close()


class Exercise:
    """This class represents a single exercise."""

    def __init__(self, name, rep, weight=None):
        """
        Constructor.

        :param name: name of the exercise
        :param rep: repetition of the exercise
        :param weight: weight of the exercise
        """
        self.name = name
        self.rep = rep
        self.weight = weight

    def __repr__(self):
        return " ".join([self.name, self.rep, str(self.weight)])


class Routine:
    """A list of exercises."""

    def __init__(self, name, exercise_list=None):
        if exercise_list is None:
            exercise_list = []
        self.name = name
        self.exercise_list = exercise_list

    def add_exercise(self, exercise):
        self.exercise_list.append(exercise)

    def delete_exercise(self, exercise):
        self.exercise_list.remove(exercise)

    def __repr__(self):
        return self.name
