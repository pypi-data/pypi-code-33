
import asyncio
import datetime
import json
import logging

from colibris import taskqueue

from testmyesp import constants
from testmyesp import flashimages
from testmyesp import models
from testmyesp import testcases

from testmyesp.hw import espctl
from testmyesp.hw import gpio

logger = logging.getLogger(__name__)


def run_job(job):
    job.logger.debug('flashing started')
    job.state = constants.JOB_STATE_FLASHING
    job.started_moment = datetime.datetime.utcnow()
    job.save()

    espctl.initial_setup()
    espctl.set_boot_mode(espctl.BOOT_MODE_FLASH)
    espctl.power_on()

    flashimages.write_flash_images(job)

    espctl.set_boot_mode(espctl.BOOT_MODE_NORMAL)
    espctl.reset()

    job.logger.debug('execution started')
    job.state = constants.JOB_STATE_EXECUTING
    job.save()

    results = testcases.run_test_cases(job)
    failed = len([r for r in results if not r.passed]) > 0

    job.logger.debug(['succeeded', 'failed'][failed])
    job.state = constants.JOB_STATE_FAILED if failed else constants.JOB_STATE_SUCCEEDED
    job.ended_moment = datetime.datetime.utcnow()
    job.results_json = json.dumps([r.to_dict() for r in results])
    job.save()

    espctl.power_off()

    job.logger.debug('closing GPIO controller')
    gpio.get_gpio_controller().close()


async def exec_loop():
    while True:
        try:
            jobs = models.Job.select()
            jobs = jobs.where(models.Job.state == constants.JOB_STATE_PENDING)
            jobs = jobs.order_by(models.Job.added_moment.asc())

            if len(jobs) == 0:
                await asyncio.sleep(1)
                continue

            job = jobs[0]
            job.logger.debug('scheduling')

            try:
                await taskqueue.execute(run_job, job, timeout=job.timeout)
                job.logger.debug('done')
                continue

            except taskqueue.TimeoutException as e:
                job.logger.error(e)
                job_error = str(e)

            except Exception as e:
                job.logger.error('execution error: %s', e, exc_info=True)
                job_error = str(e)

            # re-query job since it probably was updated by the worker
            job = models.Job.select().where(models.Job.id == job.id).get()
            job.state = constants.JOB_STATE_FAILED
            job.ended_moment = datetime.datetime.utcnow()
            job.error = job_error

            job.save()

        except Exception as e:
            logger.error('task loop error: %s', e, exc_info=True)
            await asyncio.sleep(5)
