import os
import unittest

from muscle.util.database import Database
from muscle.util.errors import DuplicateRoutineNameError, \
    DuplicateExerciseError


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database("test.db")

    def tearDown(self):
        self.db.close()
        os.remove("test.db")

    def test_init(self):
        table_names = self.db.cursor.execute("SELECT name FROM sqlite_master")
        table_names = [name_tuple[0] for name_tuple in table_names]
        self.assertTrue('exercise_table' in table_names)
        self.assertTrue('routine_table' in table_names)
        self.assertTrue('workout_record' in table_names)
        self.assertTrue('exercise_routine' in table_names)

    def test_insert_exercise(self):
        self.db.insert_exercise("bench press", "3x5")
        self.db.insert_exercise("bench press", "3x5")
        exercises = self.db.cursor.execute("SELECT * FROM exercise_table")
        exercises = exercises.fetchall()
        self.assertEqual(1, len(exercises))
        self.assertEqual(exercises[0], (1, 'bench press', '3x5'))

    def test_insert_routine(self):
        self.db.insert_routine("day1")
        routines = self.db.cursor.execute("SELECT * FROM routine_table")
        self.assertEqual(routines.fetchone(), (1, 'day1'))
        with self.assertRaises(DuplicateRoutineNameError):
            self.db.insert_routine("day1")

    def test_insert_exercise_routine(self):
        self.db.insert_exercise_routine(3, 5)
        ex_ro = self.db.cursor.execute("SELECT * FROM exercise_routine")
        self.assertEqual(ex_ro.fetchone(), (1, 3, 5))
        with self.assertRaises(DuplicateExerciseError):
            self.db.insert_exercise_routine(3, 5)

    def test_insert_workout_record(self):
        self.db.insert_workout_record("2019-01-01", 2, 1, 80)
        records = self.db.cursor.execute("SELECT * FROM workout_record")
        self.assertEqual(records.fetchone(), (1, "2019-01-01", 2, 1, 80))

    def test_exercise_id(self):
        self.db.insert_exercise("bench press", "3x5")
        exercise_id = self.db.exercise_id("bench press", "3x5")
        self.assertEqual(exercise_id, 1)

    def test_routine_id(self):
        self.db.insert_routine("day A")
        routine_id = self.db.routine_id("day A")
        self.assertEqual(routine_id, 1)

    def test_del_routine_from_ex_rout(self):
        self.db.insert_routine("dayA")
        self.db.insert_exercise_routine(3, 1)
        self.db.insert_exercise_routine(1, 1)
        self.db.insert_exercise_routine(3, 6)
        self.db.del_routine_from_ex_rout("dayA")
        select_all = self.db.cursor.execute("SELECT * FROM exercise_routine")
        self.assertEqual(1, len(select_all.fetchall()))

    def test_del_from_routine_table(self):
        self.db.insert_routine("dayA")
        self.db.insert_routine("dayB")
        self.db.del_from_routine_table("dayA")
        select_all = self.db.cursor.execute("SELECT * FROM routine_table")
        self.assertEqual(1, len(select_all.fetchall()))

    def test_mark_routine_deleted(self):
        self.db.insert_routine("dayA")
        self.db.insert_routine("dayB")
        self.db.insert_workout_record("2019-01-01", 3, 1, 80)
        self.db.insert_workout_record("2019-01-01", 2, 1, 80)
        self.db.insert_workout_record("2019-01-01", 4, 1, 80)
        self.db.insert_workout_record("2019-01-03", 1, 2, 80)
        self.db.insert_workout_record("2019-01-03", 7, 2, 80)
        self.db.insert_workout_record("2019-01-03", 6, 2, 80)
        self.db.mark_routine_deleted("dayA")
        routine_ids = self.db.cursor.execute("""
        SELECT routine_id FROM workout_record
        """).fetchall()
        routine_ids = [routine_id[0] for routine_id in routine_ids]
        for i in range(3):
            self.assertEqual(routine_ids[i], None)

    def test_list_exercises(self):
        self.db.insert_exercise("squat", "3x5")
        self.db.insert_exercise("bench press", "3x5")
        self.db.insert_exercise("deadlift", "1x5")
        self.db.insert_exercise("press", "3x5")
        self.db.insert_routine("dayA")
        self.db.insert_routine("dayB")
        self.db.insert_exercise_routine(1, 1)
        self.db.insert_exercise_routine(2, 1)
        self.db.insert_exercise_routine(3, 1)
        self.db.insert_exercise_routine(1, 2)
        self.db.insert_exercise_routine(4, 2)
        self.db.insert_exercise_routine(3, 2)
        exercise_list = self.db.list_exercises("dayA")
        self.assertEqual('squat', exercise_list[0][0])
        self.assertEqual('3x5', exercise_list[0][1])
        self.assertEqual('bench press', exercise_list[1][0])
        self.assertEqual('3x5', exercise_list[1][1])
        self.assertEqual('deadlift', exercise_list[2][0])
        self.assertEqual('1x5', exercise_list[2][1])
        exercise_list = self.db.list_exercises("dayB")
        self.assertEqual('squat', exercise_list[0][0])
        self.assertEqual('3x5', exercise_list[0][1])
        self.assertEqual('press', exercise_list[1][0])
        self.assertEqual('3x5', exercise_list[1][1])
        self.assertEqual('deadlift', exercise_list[2][0])
        self.assertEqual('1x5', exercise_list[2][1])

    def test_list_routines(self):
        self.db.insert_routine("routine1")
        self.db.insert_routine("routine2")
        self.db.insert_routine("routine3")
        routine_names = self.db.list_routines()
        self.assertEqual(['routine1', 'routine2', 'routine3'], routine_names)

    def test_last_record_date(self):
        self.db.insert_workout_record("2019-01-01", 2, 1, 80)
        self.db.insert_workout_record("2019-01-02", 2, 1, 80)
        self.db.insert_workout_record("2019-01-03", 2, 1, 80)
        self.db.insert_workout_record("2019-01-04", 2, 1, 80)
        self.db.insert_exercise("squat", "3x5")
        last_record_date = self.db.last_record_date()
        self.assertEqual('2019-01-04', last_record_date)


if __name__ == '__main__':
    unittest.main()
