import sqlite3

from muscle.util.errors import DuplicateRoutineNameError, \
    DuplicateExerciseError


class Database:
    """
    This class represents the sqlite database.

    It provides methods to interact with the sqlite database to be used by the
    model
    """

    def __init__(self, path):
        """
        Initialize a database connection.

        :param path: a PathLike object
        """
        self.conn = sqlite3.connect(path, isolation_level=None)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        """Initialize tables if they don't exist."""
        self.init_exercise_table()
        self.init_routine_table()
        self.init_workout_record_table()
        self.init_exercise_routine_table()

    def init_exercise_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_table(
        exercise_id INTEGER PRIMARY KEY NOT NULL,
        exercise TEXT NOT NULL,
        rep TEXT NOT NULL,
        unique (exercise, rep))
        """)

    def init_routine_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS routine_table(
        routine_id INTEGER PRIMARY KEY NOT NULL,
        routine TEXT NOT NULL,
        unique (routine))
        """)

    def init_workout_record_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_record(
        workout_id INTEGER PRIMARY KEY NOT NULL,
        date TEXT NOT NULL,
        exercise_id INTEGER NOT NULl,
        routine_id INTEGER,
        weight INTEGER NOT NULL)
        """)

    def init_exercise_routine_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_routine(
        ex_rt_id INTEGER PRIMARY KEY,
        exercise_id INTEGER NOT NULL,
        routine_id INTEGER NOT NULL,
        unique (exercise_id, routine_id))
        """)

    def insert_exercise(self, exercise, rep):
        try:
            """Insert an exercise into exercise_table."""
            self.cursor.execute("""
            INSERT INTO exercise_table
            (exercise, rep)
            VALUES
            (?,?)
            """, (exercise, rep))
        except sqlite3.IntegrityError:
            pass

    def insert_routine(self, routine_name):
        """Insert a routine into routine_table."""
        try:
            self.cursor.execute("""
            INSERT INTO routine_table
            (routine)
            VALUES
            (?)
            """, (routine_name,))
        except sqlite3.IntegrityError:
            raise DuplicateRoutineNameError()

    def insert_exercise_routine(self, exercise_id, routine_id):
        """Insert into exercise_routine junction table."""
        try:
            self.cursor.execute("""
            INSERT INTO exercise_routine
            (exercise_id, routine_id)
            VALUES
            (?,?)
            """, (exercise_id, routine_id))
        except sqlite3.IntegrityError:
            raise DuplicateExerciseError()

    def insert_workout_record(self, date, exercise_id, routine_id, weight):
        """Insert into workout_record table."""
        self.cursor.execute("""
        INSERT INTO workout_record
        (date, exercise_id, routine_id, weight)
        VALUES
        (?,?,?,?)
        """, (date, exercise_id, routine_id, weight))

    def exercise(self, exercise_id):
        """
        Return the name and rep of an exercise from exercise_table.

        :param exercise_id: the exercise_id
        :return: a tuple in the format of (exercise, rep)
        """
        self.cursor.execute("""
        SELECT exercise, rep FROM exercise_table
        WHERE exercise_id = ?
        """, (exercise_id,))
        return self.cursor.fetchone()

    def exercise_id(self, exercise, rep):
        """Return the exercise_id of an exercise."""
        self.cursor.execute("""
        SELECT exercise_id FROM exercise_table
        WHERE exercise = ? AND rep = ?
        """, (exercise, rep))
        return self.cursor.fetchone()[0]

    def routine_name(self, routine_id):
        """Return the name of a routine from routine_table."""
        self.cursor.execute("""
        SELECT routine FROM routine_table
        WHERE routine_id = ?
        """, (routine_id,))
        return self.cursor.fetchone()

    def routine_id(self, routine_name):
        """Return the routine_id of a routine"""
        self.cursor.execute("""
        SELECT routine_id FROM routine_table
        WHERE routine = ?
        """, (routine_name,))
        return self.cursor.fetchone()[0]

    def list_exercises(self, routine_name):
        """
        Return a list of exercises given a routine_name

        :param routine_name: name of the routine
        :return: a list of tuples (exercise, rep), ordered by exercise_id
        """
        routine_id = self.routine_id(routine_name)
        self.cursor.execute("""
        SELECT exercise_table.exercise, exercise_table.rep
        FROM exercise_table
        NATURAL JOIN
        (SELECT exercise_id, ex_rt_id FROM exercise_routine WHERE routine_id = ?)
        ORDER BY ex_rt_id
        """, (routine_id,))
        return self.cursor.fetchall()

    def list_routines(self):
        """
        Return a list of routines from routine_table

        :return: a list of routine names, ordered by routine_id
        """
        self.cursor.execute("""
        SELECT routine FROM routine_table
        ORDER BY routine_id 
        """)
        return [name[0] for name in self.cursor.fetchall()]

    def workout_record(self):
        self.cursor.execute("""
        SELECT date, exercise_id, routine_id, weight
        FROM workout_record
        ORDER BY workout_id
        """)
        return self.cursor.fetchall()

    def del_routine_from_ex_rout(self, routine_name):
        """Delete all rows from exercise_table associated with routine_name."""
        routine_id = self.routine_id(routine_name)
        self.cursor.execute("""
        DELETE FROM exercise_routine
        WHERE routine_id = ?
        """, (routine_id,))

    def del_from_routine_table(self, routine_name):
        """Delete a routine from routine_table."""
        self.cursor.execute("""
        DELETE FROM routine_table
        WHERE routine = ?
        """, (routine_name,))

    def del_from_workout_record(self, date):
        """Delete rows from workout_record on a given date."""
        self.cursor.execute("""
        DELETE FROM workout_record
        WHERE date = ?
        """, (date,))

    def mark_routine_deleted(self, routine_name):
        """Update routine_id to NULL to mark deleted routine."""
        routine_id = self.routine_id(routine_name)
        self.cursor.execute("""
        UPDATE workout_record
        SET routine_id = NULL
        WHERE routine_id = ?
        """, (routine_id,))

    def last_record_date(self):
        """Return the last record's date."""
        self.cursor.execute("""
        SELECT date FROM workout_record
        ORDER BY workout_id DESC
        LIMIT 1
        """)
        return self.cursor.fetchone()[0]

    def update_routine_id_in_workout_record(self, date, routine_id):
        """Update routine_id in workout_record table on a date."""
        self.cursor.execute("""
        UPDATE workout_record
        SET routine_id = ?
        WHERE date = ?
        """, (routine_id, date,))

    def close(self):
        """Close the database connection."""
        self.conn.close()
