import os
import unittest

from muscle.model.model import Model, Exercise, Routine
from muscle.util.errors import DuplicateRoutineNameError


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = Model('user.db')
        ex1 = Exercise('squat', '3x5')
        ex2 = Exercise('bench press', '3x5')
        ex3 = Exercise('deadlift', '1x5')
        ex4 = Exercise('press', '3x5')
        self.model.add_routine(Routine('dayA', [ex1, ex2, ex3]))
        self.model.add_routine(Routine('dayB', [ex1, ex4, ex3]))

    def tearDown(self):
        self.model.close_database_connection()
        os.remove("user.db")

    def test_add_routine(self):
        ex1 = Exercise("squat", "3x5")
        ex2 = Exercise("bench press", "3x5")
        ex3 = Exercise("deadlift", "1x5")
        with self.assertRaises(DuplicateRoutineNameError):
            self.model.add_routine(Routine("dayA", [ex1, ex2, ex3]))

        ex1_weight = Exercise("squat", "3x5", 100)
        ex2_weight = Exercise("bench press", "3x5", 200)
        ex3_weight = Exercise("deadlift", "1x5", 300)
        date = '2019-01-01'
        for ex in [ex1_weight, ex2_weight, ex3_weight]:
            self.model.record(date, ex, 'dayA')
        self.assertEqual('dayA', self.model.workout_history[date][0])
        self.model.delete_routine('dayA')
        self.assertEqual('deleted', self.model.workout_history[date][0])
        self.model.add_routine(Routine('dayA', [ex1, ex2, ex3]))
        self.assertEqual('dayA', self.model.workout_history[date][0])
        workout_history = self.model.init_workout_history()
        self.assertEqual('dayA', workout_history[date][0])

    def test_init_routine_list(self):
        routine_list = self.model.init_routine_list()
        self.assertEqual('dayA', routine_list[0].name)
        self.assertEqual('dayB', routine_list[1].name)
        self.assertEqual('squat', routine_list[0].exercise_list[0].name)
        self.assertEqual('press', routine_list[1].exercise_list[1].name)
        self.assertEqual('deadlift', routine_list[1].exercise_list[2].name)

    def test_init_workout_history(self):
        self.model.db.insert_workout_record('2019-01-01', 1, 1, 120)
        self.model.db.insert_workout_record('2019-01-01', 2, 1, 200)
        self.model.db.insert_workout_record('2019-01-01', 3, 1, 150)
        records = self.model.init_workout_history()
        self.assertTrue('2019-01-01' in records)
        self.assertEqual('dayA', records['2019-01-01'][0])
        self.assertEqual('bench press', records['2019-01-01'][2].name)

    def test_delete_record(self):
        ex1 = Exercise("squat", "3x5", 120)
        ex2 = Exercise("bench press", "3x5", 300)
        ex3 = Exercise("deadlift", "1x5", 200)
        self.model.record('2019-01-01', ex1, "dayA")
        self.model.record('2019-01-01', ex2, "dayA")
        self.model.record('2019-01-02', ex3, "dayA")
        self.model.delete_record('2019-01-01')
        records = self.model.init_workout_history()
        self.assertEqual(1, len(records))
        self.assertEqual('dayA', records['2019-01-02'][0])
        self.assertEqual('deadlift', records['2019-01-02'][1].name)


if __name__ == '__main__':
    unittest.main()
