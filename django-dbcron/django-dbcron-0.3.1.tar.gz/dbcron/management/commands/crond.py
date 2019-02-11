import time
import logging
from io import StringIO
from concurrent import futures

from django.core.management.base import BaseCommand, CommandError

from dbcron import models
from dbcron import settings
from dbcron import signals


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-t', '--tags', nargs='*',
            help='Filter jobs by tag(s)'
        )
        parser.add_argument(
            '-q', '--quiet', action='store_true',
            help='Disable any output (except logs)',
        )

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger('dbcron')
        return self._logger

    def stop(self):
        """Helper for tests"""
        return False

    def run_job(self, job):
        """Decides to run a job, launches it and handles errors."""
        # Time decision
        next_ = int(job.entry.next())
        if next_ != 0:
            self.logger.debug("%s will run in %ssec", job.name, next_)
            return
        # Run
        self.logger.info("started %s", job.name)
        signals.job_started.send(sender=self.__class__, job=job)
        try:
            result = job.run()
        except Exception as err:
            self.logger.exception("error with %s", job.name)
            signals.job_failed.send(sender=self.__class__, job=job)
            raise
        else:
            signals.job_done.send(sender=self.__class__, job=job)
        finally:
            self.logger.info("finished %s", job.name)
        return result

    def main(self, executor, tags, **kwargs):
        """Infinite loop acting as cron daemon."""
        # Lazy filtering
        jobs = models.Job.objects.filter(is_active=True)
        if tags:
            jobs = jobs.filter(tag__in=tags)
        self.stdout.write(self.style.SUCCESS('Started'))
        # Main Loop
        while True:
            self.logger.debug("new loop")
            executor.map(self.run_job, jobs.all())
            if self.stop():
                break
            time.sleep(1)

    def handle(self, *args, **options):
        if options['quiet']:
            self.stdout = self.stdout = StringIO()
        executor = futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
        try:
            self.main(executor, **options)
        except KeyboardInterrupt as err:
            executor.shutdown()
            self.stdout.write(self.style.WARNING('Stopped'))
            return
