""" A ScheduleRunCommand Command """
from cleo import Command
from scheduler.Task import Task
import pendulum


class ScheduleRunCommand(Command):
    """
    Run the scheduled tasks

    schedule:run
        {--t|task=None : Name of task you want to run}
    """

    def handle(self):
        from wsgi import container as app
        tasks = app.collect(Task)
        
        for task_key, task_class in tasks.items():
            # Resolve the task with the container
            if self.option('task') != 'None':
                if self.option('task') != task_key and self.option('task') != task_class.name:
                    continue

            task = app.resolve(task_class)

            # If the class should run then run it
            if task.should_run():
                task.handle()
