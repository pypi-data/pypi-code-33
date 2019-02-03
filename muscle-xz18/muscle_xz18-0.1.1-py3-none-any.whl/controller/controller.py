import shutil
from datetime import datetime
from pathlib import Path, PosixPath

from muscle.model.model import Model, Routine
from muscle.util.errors import DatabaseNotFoundError, RecordAlreadyEnteredError


class Controller:

    def __init__(self, database_path=None):
        """
        Initialize a controller.

        :param database_path: the location of the database file
        default location: ~/.local/share/muscle/user.db
        """
        if database_path is None:
            data_dir = Path.home().joinpath('.local/share/muscle')
            data_dir.mkdir(parents=True, exist_ok=True)
            database_path = data_dir.joinpath('user.db')
        self.model = Model(str(database_path))

    def add_routine(self, routine_name, exercise_list):
        """
        Add a new routine

        :param routine_name: the name of the new routine
        :param exercise_list: a list of Exercise objects
        :raises DuplicateRoutineNameError: if there's duplicate routine name
        :raises DuplicateExerciseError: if there's duplicate exercise
        """
        routine = Routine(routine_name)
        for exercise in exercise_list:
            routine.add_exercise(exercise)
        self.model.add_routine(routine)

    def list_routines(self):
        """Return a list of routines."""
        return self.model.routine_list

    def list_exercises(self, routine_name):
        """
        Return a list of exercises given a routine_name.

        :param routine_name: the routine_name to list exercises
        :raises RoutineNotFoundError: if the routine_name doesn't exist
        """
        return self.model.list_exercises(routine_name)

    def record(self, exercise_list, routine_name):
        """
        Record today's workout.

        :param exercise_list: a list of today's exercises, weight can't be None
        :param routine_name: name of the routine
        :raises RecordAlreadyEnteredError: if a record already exists for today
        """
        date = datetime.today().date().__str__()
        if date in self.model.workout_history:
            raise RecordAlreadyEnteredError
        for exercise in exercise_list:
            self.model.record(date, exercise, routine_name)

    def workout_history(self):
        """
        Return workout history as a dict.

        :return: a dict this format {date: [routine_name, exercise...]}
        """
        return self.model.workout_history

    def delete_record(self, date):
        """
        Delete a record given a date.

        :param date: a string in this format YYYY-MM-DD
        """
        self.model.delete_record(date)

    def delete_routine(self, routine_name):
        """
        Delete a routine.

        :param routine_name: name of the routine to be deleted
        :raises RoutineNotFoundError: if the routine_name doesn't exist
        """
        self.model.delete_routine(routine_name)

    def last_record_date(self):
        """
        Return the last record's date.

        :return: a string in this format YYYY-MM-DD
        """
        return self.model.last_record_date()

    def workout_history_is_empty(self):
        """
        Check if workout history is empty.

        :return: True if empty, False otherwise
        """
        return len(self.model.workout_history) == 0

    def routine_list_is_empty(self):
        """
        Check if routine list is empty.

        :return: True if empty, False otherwise
        """
        return len(self.model.routine_list) == 0

    def terminate(self):
        self.model.close_database_connection()

    def import_db(self, path):
        import_path = PosixPath(path).expanduser()
        if not import_path.exists():
            raise DatabaseNotFoundError
        new_model = Model(str(import_path))
        default_path = Path.home().joinpath('.local/share/muscle/user.db')
        shutil.copy2(str(import_path), str(default_path))
        self.model = new_model

    def export_db(self, path):
        target_path = PosixPath(path).expanduser()
        default_path = Path.home().joinpath('.local/share/muscle/user.db')
        shutil.copy2(str(default_path), str(target_path))
