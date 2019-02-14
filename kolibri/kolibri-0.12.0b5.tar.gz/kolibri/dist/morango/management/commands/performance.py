"""
Management command designed to test the performance of core operations in morango (serialization, buffering, dequeuing, deserialization).
Need to define a profile and filter on the Command class (done in setUp).
"""


from __future__ import print_function

import atexit
import json
import time
import uuid

from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models
from morango import models as m_models
from morango.models import (Buffer, DeletedModels, InstanceIDModel, Store,
                            SyncSession, TransferSession)
from morango.util import syncable_model_count
from morango.utils.register_models import _profile_models
from morango.utils.sync_utils import (_dequeue_into_store,
                                      _deserialize_from_store,
                                      _queue_into_buffer,
                                      _serialize_into_store)

f = open('performance.log', 'w')


class Timer(object):

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs

def time_function(message, function, *args, **kwargs):
    with Timer() as timer:
        function(*args, **kwargs)
    print("=> Elapsed {}: {} seconds".format(message, timer.secs))
    return timer

def median(lst):
    n = len(lst)
    if n < 1:
        return None
    if n % 2 == 1:
        return sorted(lst)[n//2]
    else:
        return sum(sorted(lst)[n//2-1:n//2+1])/2.0


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        pass
        # atexit.register(self.cleanUpDB)

    def add_arguments(self, parser):
        parser.add_argument('--outer-runs', type=int, default=1, help='Number of times to run outerloop benchmarking (recommended after tearing down some models')
        parser.add_argument('--inner-runs', type=int, default=3, help='Number of times to run innerloop benchmarking (recommended for several iterations to get median)')

    def setUp(self, *args, **options):
        raise NotImplementedError("Must override the method `setUp` and instantiate your syncable models")

    def handle(self, *args, **options):
        destination_db = settings.DATABASES.get('default')
        db_backend = destination_db['ENGINE'].split(".")[-1]
        print("Running with database backend {} on {}\n".format(db_backend, timezone.now()), file=f)

        self.setUp(*args, **options)
        print("Beginning performance benchmarking...\n")

        for outer_runs in range(options['outer_runs']):
            print("Outer loop run {}".format(outer_runs + 1))
            print("=================")

            l_serialization = []
            l_buffering = []
            l_dequeuing = []
            l_deserialization = []
            total_time = []

            for inner_runs in range(options['inner_runs']):
                print("Inner loop run {}".format(inner_runs + 1))
                print("Setting up initial models...")
                InstanceIDModel.get_or_create_current_instance()

                # SERIALIZATION of app models into store
                models_count = syncable_model_count(self.profile, filters=self.filters)
                print("Benchmarking with {} model(s)".format(models_count))

                serialization = time_function("Serialization", _serialize_into_store, profile=self.profile)
                l_serialization.append(serialization.secs)
                store_count = Store.objects.count()

                assert models_count == store_count, "Number of model records: {} does not match number of store records: {}!".format(models_count, store_count)
                # create relevant session models necessary for sync like operations
                id_model, _ = InstanceIDModel.get_or_create_current_instance()
                ss = SyncSession.objects.create(id=uuid.uuid4().hex, profile=self.profile, last_activity_timestamp=timezone.now())
                ts = TransferSession.objects.create(id=uuid.uuid4().hex,
                                                    push=True,
                                                    filter=self.filters,
                                                    sync_session=ss,
                                                    last_activity_timestamp=timezone.now(),
                                                    client_fsic=json.dumps({id_model.id: id_model.counter}))

                # BUFFERING store records into buffer
                buffering = time_function("Buffering", _queue_into_buffer, ts)
                l_buffering.append(buffering.secs)
                buffer_count = Buffer.objects.count()

                assert store_count == buffer_count, "Number of store records: {} does not match number of buffered records: {}!".format(store_count, buffer_count)
                # clear store models
                Store.objects.all().delete()

                # DEQUEUING buffered records into store
                dequeuing = time_function("Dequeuing", _dequeue_into_store, ts)
                l_dequeuing.append(dequeuing.secs)
                store_count = Store.objects.count()

                assert store_count == buffer_count, "Number of store records: {} does not match number of buffered records: {}!".format(store_count, buffer_count)
                # clear all syncable models
                for klass in _profile_models[self.profile].values():
                    klass.objects.all().delete()
                DeletedModels.objects.all().delete()
                Store.objects.update(dirty_bit=True)

                # DESERIALIZATION of store models into app layer
                deserialization = time_function("Deserialization", _deserialize_from_store, profile=self.profile)
                l_deserialization.append(deserialization.secs)
                models_count = syncable_model_count(self.profile, filters=self.filters)

                assert store_count == models_count, "Number of model records: {} does not match number of store records: {}!".format(models_count, store_count)

                total_time.append(serialization.secs + buffering.secs + dequeuing.secs + deserialization.secs)
                print("=> TOTAL ELAPSED TIME: {}s".format(total_time[inner_runs]))

                # clean up before next run
                print("Resetting database models...\n")
                Store.objects.all().delete()
                for klass in _profile_models[self.profile].values():
                    klass.objects.update(_morango_dirty_bit=True)

            print("MEDIAN TIMES AFTER {} RUNS WITH {} MODELS...".format(options['inner_runs'], models_count), file=f)
            print("===========================================", file=f)
            print("Serialization: {}s".format(median(l_serialization)), file=f)
            print("Buffering: {}s".format(median(l_buffering)), file=f)
            print("Dequeuing: {}s".format(median(l_dequeuing)), file=f)
            print("Deserialization: {}s".format(median(l_deserialization)), file=f)
            print("=> TOTAL ELAPSED TIME: {}s\n".format(median(total_time)), file=f)
            self.tearDown()
        f.close()

    def tearDown(self):
        pass

    # def cleanUpDB(self):
    #     """
    #     Clean up database from this management command run.
    #     """
    #     # clear all syncable models
    #     for klass in _profile_models['facilitydata'].values():
    #         klass.objects.all().delete()

    #     # clear all morango models
    #     [cls.objects.all().delete() for _, cls in m_models.__dict__.items() if isinstance(cls, models.base.ModelBase) and not cls._meta.abstract]
