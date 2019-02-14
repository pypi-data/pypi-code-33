import os
import time

from skidward import JobStatus
# import before skidward.models to avoid circular imports
from skidward import web
from skidward.backend import RedisBackend
from skidward.models import db, Job


WAKEUP_TIMER = int(os.getenv("WAKEUP_TIMER"))


def job_exists(job, redis_client):
    jobs = redis_client.lrange("jobs", 0, -1)
    return str(job).encode("utf-8") in jobs


def add_jobs_to_redis(redis_client, jobs, session):

    for job in jobs:
        if not job_exists(job, redis_client):
            redis_client.lpush("jobs", job)
            db_job = session.query(Job).filter(Job.id == job)
            db_job.update({"state": JobStatus.RUNNING})
            session.commit()


def get_jobs(redis_backend):
    jobs = db.session.query(Job).filter(Job.state == JobStatus.READY)

    jobs_id = [job.id for job in jobs]

    if jobs_id:
        add_jobs_to_redis(redis_backend, jobs_id, db.session)
    else:
        print("No job ready to run")


def main():

    redis_backend = RedisBackend()
    while True:
        get_jobs(redis_backend)
        time.sleep(WAKEUP_TIMER)


if __name__ == "__main__":
    main()
