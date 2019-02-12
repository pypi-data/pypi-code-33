import threading
import concurrent.futures
import tempfile
import logging
import uuid
import os

from datapackage_pipelines.manager import ProgressReport, run_pipelines
from datapackage_pipelines.manager.runner import match_pipeline_id
from datapackage_pipelines.specs import pipelines, PipelineSpec
from datapackage_pipelines.status import status_mgr


class DppRunner:

    def __init__(self, max_workers=8):
        self.running = {}
        self.rlock = threading.RLock()
        self.pool = \
            concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def specs(self, argument, root_dir, ignore_missing_deps=False):
        status_manager = status_mgr(root_dir)
        specs = []
        for spec in pipelines(ignore_missing_deps=ignore_missing_deps,
                              root_dir=root_dir,
                              status_manager=status_manager):
            if match_pipeline_id(argument, spec.pipeline_id):
                specs.append(spec)

        return specs

    def _run_in_background(self, uid, dirname, verbosity=0, status_cb=None):

        if hasattr(status_cb, 'init_progress'):
            specs = self.specs('all', dirname)
            status_cb.init_progress(specs)

        def progress_cb(pr: ProgressReport):
            with self.rlock:
                pipeline_id, row_count, success, errors, stats = pr
                if verbosity > 0:
                    logging.info('Callback %s #%d (success: %s, errors: %r, stats: %s)',
                                 pipeline_id, row_count, success, errors,
                                 stats)
                current = self.running[uid]['progress'].get(pipeline_id)
                self.running[uid]['progress'].update({
                    pipeline_id: dict(
                        done=success is not None,
                        success=success,
                        rows=row_count,
                        errors=errors,
                        stats=stats
                    )
                })
                if status_cb:
                    if current is None:
                        status_cb(pipeline_id, 'INPROGRESS')
                    else:
                        if success is not None:
                            status_cb(pipeline_id,
                                      'SUCCESS' if success else 'FAILED',
                                      errors=errors, stats=stats)

        try:
            if verbosity > 0:
                logging.info('Running all pipelines')
            results = run_pipelines('all',
                                    dirname,
                                    use_cache=False,
                                    dirty=False,
                                    force=False,
                                    concurrency=999,
                                    verbose_logs=verbosity > 1,
                                    progress_cb=progress_cb)
            if verbosity > 0:
                logging.info('Running complete')
            with self.rlock:
                self.running[uid]['results'] = [
                    p._asdict()
                    for p in results
                ]
                if verbosity > 0:
                    logging.info('Results %r', self.running[uid])
        except Exception as e:
            logging.exception('Failed to run pipelines')
        finally:
            self.running[uid]['dir'].cleanup()
            del self.running[uid]['dir']

    def start(self, kind, data, verbosity=0, status_cb=None):
        if kind is None:
            filename = 'pipeline-spec.yaml'
        else:
            filename = kind + '.source-spec.yaml'

        tempdir = tempfile.TemporaryDirectory()
        with open(os.path.join(tempdir.name, filename), 'wb') as spec:
            spec.write(data)

        uid = uuid.uuid4().hex

        self.running[uid] = dict(
            dir=tempdir,
            results={},
            progress={}
        )

        self.pool.submit(self._run_in_background, uid,
                         tempdir.name, verbosity, status_cb)

        return uid

    def status(self, uid):
        with self.rlock:
            ret = self.running.get(uid, {})
            ret = dict(
                results=ret.get('results'),
                progress=ret.get('progress')
            )
            return ret
