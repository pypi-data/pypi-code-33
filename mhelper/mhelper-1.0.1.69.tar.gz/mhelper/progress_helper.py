import time
from typing import Optional


class ProgressMaker:
    def __init__( self, total, issue, delay = 1 ):
        self.total_jobs = total
        self.start_time = time.perf_counter()
        self.issue_function = issue
        self.delay = delay
        self.next = self.start_time + delay
    
    
    def report( self, processed ) -> Optional["Progress"]:
        if self.delay:
            now = self.start_time
            
            if now < self.next:
                return None
            
            self.next = now + self.delay
        
        p = Progress( processed, self.total_jobs, self.start_time, time.perf_counter() )
        self.issue_function( p )
        return p


class Progress:
    def __init__( self, total, processed, start, now ):
        """
        
        :param total:       Total number of jobs 
        :param processed:   Number of jobs completed 
        :param start:       Start time 
        :param now:         Time now 
        """
        self.processed_jobs = processed
        self.total_jobs = total
        self.start_time = start
        self.current_time = now
        self.elapsed_time = now - start
        
        self.remaining_jobs = (self.total_jobs - self.processed_jobs) if self.total_jobs else 0
        self.time_per_job = (self.elapsed_time / self.processed_jobs) if self.processed_jobs else 0
        self.remaining_time = self.remaining_jobs * self.time_per_job
        
        self.fraction_complete = (self.processed_jobs / self.total_jobs) if self.total_jobs else 0
        self.percent_complete = self.fraction_complete * 100
