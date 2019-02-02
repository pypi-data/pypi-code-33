import os
import unittest
from datetime import datetime

from muscle.controller.controller import Controller
from muscle.model.model import Exercise
from muscle.util.errors import DuplicateRoutineNameError, \
    RecordAlreadyEnteredError


class TestController(unittest.TestCase):

    def setUp(self):
        self.controller = Controller('user.db')
        self.ex1 = Exercise("squat", "3x5")
        self.ex2 = Exercise("bench press", "3x5")
        self.ex3 = Exercise("deadlift", "1x5")
        self.ex4 = Exercise("press", "3x5")
        self.controller.add_routine("dayA", [self.ex1, self.ex2, self.ex3])

    def tearDown(self):
        self.controller.terminate()
        os.remove("user.db")

    def test_add_routine(self):
        with self.assertRaises(DuplicateRoutineNameError):
            self.controller.add_routine("dayA", [self.ex2, self.ex1, self.ex3])

        routine_list = self.controller.list_routines()
        routine_names = [rt.name for rt in routine_list]
        self.assertEqual(1, len(routine_names))
        self.assertEqual("dayA", routine_names[0])

    def test_list_exercises(self):
        self.controller.add_routine("dayB", [self.ex1, self.ex4, self.ex3])

        day_a_exercise = self.controller.list_exercises("dayA")
        day_b_exercise = self.controller.list_exercises("dayB")
        day_a_exercise = [ex.name for ex in day_a_exercise]
        day_b_exercise = [ex.name for ex in day_b_exercise]
        self.assertEqual(day_a_exercise, ['squat', 'bench press', 'deadlift'])
        self.assertEqual(day_b_exercise, ['squat', 'press', 'deadlift'])

    def test_record(self):
        ex1 = Exercise("squat", "3x5", 200)
        ex2 = Exercise("bench press", "3x5", 140)
        ex3 = Exercise("deadlift", "1x5", 200)
        exercise_list = [ex1, ex2, ex3]
        self.controller.record(exercise_list, "dayA")
        with self.assertRaises(RecordAlreadyEnteredError):
            self.controller.record(exercise_list, "dayA")
        records = self.controller.model.workout_history
        date = datetime.today().date().__str__()
        self.assertEqual('dayA', records[date][0])
        self.assertEqual('squat 3x5 200', str(records[date][1]))
        self.assertEqual('bench press 3x5 140', str(records[date][2]))
        self.assertEqual('deadlift 1x5 200', str(records[date][3]))

    def test_delete_routine(self):
        self.controller.add_routine("dayB", [self.ex1, self.ex4, self.ex3])
        ex1 = Exercise("squat", "3x5", 200)
        ex2 = Exercise("bench press", "3x5", 140)
        ex3 = Exercise("deadlift", "1x5", 200)
        self.controller.record([ex1, ex2, ex3], "dayA")
        self.controller.delete_routine("dayB")
        routine_list = self.controller.list_routines()
        routine_names = [rt.name for rt in routine_list]
        self.assertEqual(1, len(routine_names))
        self.assertEqual("dayA", routine_names[0])

    def test_delete_record(self):
        ex1 = Exercise("squat", "3x5", 200)
        ex2 = Exercise("bench press", "3x5", 140)
        ex3 = Exercise("deadlift", "1x5", 200)
        self.controller.record([ex1, ex2, ex3], "dayA")
        records = self.controller.model.init_workout_history()
        self.assertEqual(1, len(records))
        date = datetime.today().date().__str__()
        self.controller.delete_record(date)
        records = self.controller.model.init_workout_history()
        self.assertEqual(0, len(records))


if __name__ == '__main__':
    unittest.main()
