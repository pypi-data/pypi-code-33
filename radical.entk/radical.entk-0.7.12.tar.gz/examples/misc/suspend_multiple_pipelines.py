from radical.entk import Pipeline, Stage, Task, AppManager
import os
import sys
from time import sleep

# ------------------------------------------------------------------------------
# Set default verbosity

if not os.environ.get('RADICAL_ENTK_VERBOSE'):
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

hostname = os.environ.get('RMQ_HOSTNAME', 'localhost')
port = int(os.environ.get('RMQ_PORT', 5672))
cur_dir = os.path.dirname(os.path.abspath(__file__))
MLAB = os.environ.get('RADICAL_PILOT_DBURL')


def get_stage_1():

    s = Stage()

    t = Task()
    t.executable = ['/bin/echo']
    t.arguments = ['Stage 1']

    # Add the Task to the Stage
    s.add_tasks(t)

    return s    


def get_stage_2():

    s = Stage()

    t = Task()
    t.executable = ['/bin/echo']
    t.arguments = ['Stage 2']

    # Add the Task to the Stage
    s.add_tasks(t)

    return s    


def func_suspend(pipe):

        pipe.cnt+=1
        if (pipe.cnt-1)%2==0:
            pipe.suspend()        
        else:
            s2 = get_stage_2()
            s2.post_exec = func_resume(pipes, pipe)
            pipe.add_stages(s2)


def func_resume(pipes, cur_pipe):

    for pipe in pipes:
        s1 = get_stage_1()
        s1.post_exec = func_resume(pipe)
        pipe.add_stages(s1)
        if pipe.uid != cur_pipe.uid:
            pipe.resume()

def generate_pipeline(cnt):

    # Create a Pipeline object
    p = Pipeline()
    p.cnt = cnt

    # Add post-exec to the Stage
    s = get_stage_1()
    s.post_exec = func_suspend(pipe)

    # Add Stage to the Pipeline
    p.add_stages(s1)

    return p

pipes = list()

if __name__ == '__main__':

    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

        'resource': 'local.localhost',
        'walltime': 15,
        'cpus': 2,
    }

    # Create Application Manager
    appman = AppManager(hostname='two.radical-project.org',port=33251)
    appman.resource_desc = res_dict

    p1 = generate_pipeline()
    p2 = generate_pipeline()
    pipes.extend([p1,p2])

    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.workflow = [pipes]

    # Run the Application Manager
    appman.run()
