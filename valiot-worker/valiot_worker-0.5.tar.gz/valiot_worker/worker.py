from .utils.client import worker
import time
import json
import multiprocessing as mp
# terminal styles for better logging
import sys
from colorama import Fore, Back, Style, init as init_term, AnsiToWin32
from termcolor import colored

# colorful terminal initializacion
init_term(wrap=True, autoreset=True)
stream = AnsiToWin32(sys.stderr).stream

# print wrappers
def echo(type, message):
    if(type == 'info'):
        echo_info(message)
    if(type == 'succ'):
        echo_success(message)
    if(type == 'warn'):
        echo_warning(message)
    if(type == 'err'):
        echo_error(message)

def echo_info(message):
    print(message)

def echo_success(message):
    print(colored(message, 'green'))

def echo_warning(message):
    print(colored(message, 'yellow'))


def echo_error(message):
    print(colored(message, 'red'))

jobs = {}
schedules = {}

def job(name):
    def wrap(f):
        jobs[name] = f
        return f
    return wrap

def schedule(name):
    def wrap(f):
        schedules[name] = f
        return f
    return wrap

def not_found(job_id, update_job):
    echo('err', '     Function not found :(')

def run():
    ctx = mp.get_context('fork')
    for name, function in schedules.items():
        p = ctx.Process(
                        target=function
                        )
        p.start()
    while 1:
        time.sleep(1.0)
        try:
            success, queue = worker.request_waiting_jobs()
            if not success:
                message = queue
                echo('err', f'Error! msg: {message}')
                continue
            if queue is not None and len(queue) > 0:
                echo('warn', f"Found {len(queue)} jobs in queue")
                for job in queue:
                    # Obtiene job
                    job_fn = jobs.get(job['function'], not_found)
                    # Obtiene inputs
                    if job['input']:
                        kwargs = json.loads(job['input'])
                    else:
                        kwargs = None
                    # try to run job
                    if (worker.update_job({'id': int(job['id']),'status': 'RUNNING', 'output': ''})):
                        p = ctx.Process(
                            target=job_fn, 
                            args=(int(job['id']), worker.update_job, kwargs)
                            )
                        p.start()
                        echo('succ', f'started job with ID {job["id"]}')
            else:
                echo('warn', "Listening...")
        except Exception as e:
            echo('err', f'Request of jobs failed!')
            echo('err', f'e: {e}')
