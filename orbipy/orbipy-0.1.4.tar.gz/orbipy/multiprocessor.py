# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 17:52:14 2019

@author: stasb
"""

import numpy as np
import multiprocessing
import sys, os, time
from datetime import datetime, timedelta
import itertools

class mp:
    def __init__(self, workname, do_calc, do_save, folder=None):
        self.workname = workname
        self.do_calc = do_calc
        self.do_save = do_save
        if folder in (None, ''):
            self.folder = os.getcwd()
        else:
            self.folder = folder
        self.done_path = os.path.join(self.folder, self.workname+'_done.csv')
        self.todo_path = os.path.join(self.folder, self.workname+'_todo.csv')
    
    def run(self, p=2):
        jobs = self.get_remaining_jobs()
        self.manager = multiprocessing.Manager()
        self.queue = self.manager.Queue()
        self.pool = multiprocessing.Pool(processes=p+1)
        
        mp.mprint('<<< pool of %d workers on %d jobs started >>>'%(p, len(jobs)))
        mp.mprint('<<< use [ctrl+c] to terminate processes >>>')
        
        self.pool.apply_async(mp.save_proxy, 
                              args=(len(jobs),
                                    self.do_save,
                                    self.queue, 
                                    self.done_path, 
                                    self.folder))
        todo_jobs = [{'job':job,
                      'do_calc':self.do_calc,
                      'q':self.queue} for job in jobs]
        self.pool.map_async(mp.calc_proxy, todo_jobs)

    def mprint(*args, **kwargs):
        '''
        Print args and flush buffer so result immediately goes to console
        '''
        print(*args, **kwargs)
        sys.stdout.flush()

    def dhms(seconds):
        """Return the tuple of days, hours, minutes and seconds."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return days, hours, minutes, seconds

    def generate_jobs(**kwdata):
        return list(itertools.product(*kwdata.values()))
    
    def read_csv(path, sep=','):
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            lines = f.readlines()
        if len(lines) > 0:
            return list(map(lambda s: tuple(map(np.float64, s.strip().split(sep))), lines))
        return []
    
    def write_csv(path, jobs, sep=','):
        lines = [sep.join([str(arg) for arg in job])+'\n' for job in jobs]
        with open(path, 'wt') as f:
            f.writelines(lines)
            
    def append_csv(path, jobs, sep=','):
        lines = [sep.join([str(arg) for arg in job])+'\n' for job in jobs]
        with open(path, 'at') as f:
            f.writelines(lines)
    
    def update_todo_jobs(self, jobs):
        todo_jobs = set(mp.read_csv(self.todo_path))
        todo_jobs.update(set(jobs))
        mp.write_csv(self.todo_path, todo_jobs)
        return self

    def reset_done_jobs(self):
        if os.path.exists(self.done_path):
            os.remove(self.done_path)
        return self

    def get_remaining_jobs(self):
        todo_jobs = set(mp.read_csv(self.todo_path))
        if not todo_jobs:
            return []
        done_jobs = set(mp.read_csv(self.done_path))
        return list(todo_jobs.difference(done_jobs))
    
    def dhms_string(dt):
        '''
            dt : timedelta
        '''
        return '%02d:%02d:%02d:%05.2f'%mp.dhms(dt.total_seconds())
    
    def mprint_stat(dt, job_count, done_count, splitline='-'*32):
        avg = dt.total_seconds()/done_count
        eta = timedelta(seconds=avg*(job_count-done_count))
        fin = datetime.now()+eta
        
        mp.mprint(splitline+'\n',
                  '< AVG: %.2fs >\n'%avg,
                  '< ETA: %s >\n'%mp.dhms_string(eta),
                  '< FIN: %s >\n'%fin.strftime('%d-%b-%Y %H:%M:%S'),
                  splitline+'\n', sep='')
        
    def save_proxy(N, do_save, queue, done_path, folder):
        t0 = datetime.now()
        i = 0
        while i < N:
            if queue.empty():
                time.sleep(0.1)
            else:
                item = queue.get()
                if item['res'] is not None:                    
                    mp.mprint('< SAVE #%d/%d >'%(i,N))
                    do_save(item, folder)
                    mp.append_csv(done_path,[item['job']])
                i += 1
                if i%10 == 0:
                    dt = datetime.now()-t0
                    mp.mprint_stat(dt,N,i)
        # finishing
        dt = datetime.now()-t0
        mp.mprint_stat(dt,N,i)
        mp.mprint('<<< pool finished working on %d jobs >>>'%(N))
        
    def calc_proxy(arg):
        job = arg['job']
        do_calc = arg['do_calc']
        mp.mprint('< CALC:', job, '>')
        try:
            t0 = datetime.now()
            res = do_calc(job)
        except BaseException as e:
            mp.mprint('< EXCEPTION: %r >'%e)
            res = None
        finally:
            t = datetime.now() - t0
            mp.mprint('< JOB %r DONE >\n< CPU: %.2fs >'%(job,t.total_seconds()))
            arg['q'].put({'job':job, 'res':res})
        
    def test_calc(job):
        # actual calculation work will be done here!
#        mp.mprint('CALC [', job, ']')
        time.sleep(np.random.randint(1,5))
#        raise RuntimeError('Calculation error')
        res = job[1]*job[0]
        return res
    
    def test_save(item, folder):
        # results will be saved here
        mp.mprint('Saving result: ', item['res'], 
                  'of job:', item['job'],
                  'into folder', folder)
        pass
    
if __name__ == '__main__':
    jobs = mp.generate_jobs(x = [1,2,3,4,5], y = [6,7,8,9,10])
    m = mp('mp_test_work', 
           do_calc=mp.test_calc,
           do_save=mp.test_save).update_todo_jobs(jobs).reset_done_jobs()
    m.run(p=2)
