

class TaskQueue:
    def __init__(self):
        self.tasks = []

    def add_task(self, exe_func, *params):
        self.tasks.append((exe_func, *params))
