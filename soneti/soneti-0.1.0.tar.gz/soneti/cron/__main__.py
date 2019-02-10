import sched, time 
import os
import subprocess
import sys


if not os.path.exists('tasks.py'):
    print('ERROR! Please, create a file named {}/tasks.py with a luigi.Task named Main'.format(os.getcwd()))
    sys.exit(1)

print('Running task Main from {}/tasks.py'.format(os.getcwd()))


ORCHESTRATOR_INTERVAL = int(os.environ.get('ORCHESTRATOR_INTERVAL', 60)) # Run every minute

s = sched.scheduler(time.time, time.sleep)


def cron():
    command = 'python -m luigi --module tasks Main'
    subprocess.check_call(command.split(), shell= False)
    s.enter(ORCHESTRATOR_INTERVAL, 1, cron, [])


s.enter(0, 1, cron, [])
s.run()
