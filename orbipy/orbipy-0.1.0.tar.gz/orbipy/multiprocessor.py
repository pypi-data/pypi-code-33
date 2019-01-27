# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 12:42:16 2018

@author: stasb
"""

import multiprocessing as mp
import sys, os, time, json
from datetime import datetime
import itertools

class multiprocessor:
    
    def __init__(self, calculator, writer, filename):
        self.filename = filename
        self.calculator = calculator
        self.writer = writer
        self.listener = None
    
    def run(self, process_count=mp.cpu_count()//2):
        self.queue = mp.Queue() 
    
        listener_job = {'write_fun':self.writer, 
                        'calc_fun':self.calculator, 
                        'queue':self.queue, 
                        'jobs':self.filename, 
                        'p':process_count}
        self.listener = mp.Process(target=multiprocessor.async_listener, 
                                   args=(listener_job,))
        self.listener.start()
        
#    def kill(self):
#        if self.listener:
#            self.listener.kill()
            
    @staticmethod
    def generate_jobs(**kwdata):
        keys = kwdata.keys()
        data = kwdata.values()
        jobs = dict([(i, dict(zip(keys,job))) for i, job in enumerate(itertools.product(*data))])
        return jobs
    
    @staticmethod
    def datetime_filename(fmt='%Y%m%d_%H%M%S', ext='.jobs'):
        return datetime.now().strftime(fmt) + ext
    
    @staticmethod
    def dhms(seconds):
        """Return the tuple of days, hours, minutes and seconds."""
    
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
    
        return days, hours, minutes, seconds
        
    @staticmethod
    def save_jobs(jobs, filename):
        if os.path.exists(filename):
            pass
            #raise RuntimeWarning('File %s already exists'%filename)
        else:
            with open(filename, 'wt') as f:
                json.dump(jobs, f, indent='\t')
        return filename
    
    @staticmethod
    def async_calc(arg):
        '''    
            Asyncronous calculation starter
        '''
        t0 = datetime.now()
        arg['result']=arg['fun'](arg['job'])
        t = datetime.now() - t0
        print('<job %s done | CPU time: %.2f s>'%(arg['id'],t.total_seconds()))
        arg.pop('queue').put(arg)    
    
    @staticmethod
    def async_listener(arg):
        '''
            Asyncronous listener: writes results and runs next jobs
        '''
        write_fun = arg['write_fun']
        calc_fun = arg['calc_fun']
        q = arg['queue']
        job_file = arg['jobs']
        p = arg['p']
        workers = []
        
        t0 = datetime.now()
        
        with open(job_file, 'r') as f:
            jobs = json.load(f)
        jobs_ids = list(jobs.keys())
    
        calc_jobs = [{'fun':calc_fun, 
                      'queue':q, 
                      'id':i, 
                      'job':jobs[i]} for i in jobs_ids]
        
        first_jobs = calc_jobs[:p]
        for pid, j in enumerate(first_jobs):
            worker = mp.Process(target=multiprocessor.async_calc, 
                                args=(j,), daemon=True).start()
            workers.append(worker)
            
        calc_jobs = calc_jobs[p:]
        print('<pool of %d processes started working on %d jobs>'%(p, len(jobs)))
        print('<use [ctrl+c] to terminate processes>')
        sys.stdout.flush()
        
        jobs_done = 0
    
        while True:
            if q.empty():
                # listener should sleep or it will grab all CPU time
                time.sleep(0.1)
            else:
                jobs_done += 1
                job = q.get()
                write_fun(job)
                with open(job_file, 'r') as f:
                    jf = json.load(f)
                jf.pop(job['id'])
                with open(job_file, 'w') as f:
                    json.dump(jf, f)
                sys.stdout.flush()
                if not jf:
                    dt = datetime.now() - t0
                    print('<pool of %d processes finished working on %d jobs>'%(p, jobs_done))
                    print('<time spent: %02d:%02d:%02d:%05.2f dd:hh:mm:ss.ss (%.2f s)>' % 
                          (*multiprocessor.dhms(dt.total_seconds()),dt.total_seconds()))
                    print('<average time per job: %.2f s>'% (dt.total_seconds()/jobs_done))

                    sys.stdout.flush()
                    break
                if calc_jobs: # run next job
                    next_job = calc_jobs.pop(0)
                    mp.Process(target=multiprocessor.async_calc, 
                               args=(next_job,), daemon=True).start()
    

def writer(job):
    with open('result.txt', 'at') as f:
        f.write('%r\n'%job)
        
def calc(job):
    time.sleep(5)
    return job['y']*job['x']

#if __name__ == '__main__':       
#    
#    jobs = multiprocessor.generate_jobs(**{'x':[2,4,6,5,3,1], 'y':list('abcdef')})
#    filename = multiprocessor.save_jobs(jobs, 'jobs.json')
#    mpr = multiprocessor(calc, writer, filename)
#    mpr.run()
