import os
from os import environ
from random import randint, choice
from string import printable, whitespace
from tempfile import mkstemp
from time import sleep
from uuid import uuid4

import pytest

from pyqalx import Qalx, Bot
from pyqalx.bot import BaseBot
from pyqalx.config import UserConfig, BotConfig
from pyqalx.core.errors import QalxAPIResponseError, QalxError
from pyqalx.core.log import LOGGING_DEFAULTS
from pyqalx.transport import PyQalxAPI


def append_short_uuid(prefix, uuid_lenth=6):
    return '_'.join([prefix, uuid4().hex[:uuid_lenth]])


DEV_CONFIGS = {"BASE_URL": environ.get("QALX_TEST_URL", "A FAKE TOKEN"),
               "TOKEN": environ.get("QALX_TEST_TOKEN", "A FAKE TOKEN")}

@pytest.fixture(scope="function")
def qalx():
    q = Qalx(skip_ini=True)
    q.config.update(DEV_CONFIGS)
    q.rest_api = PyQalxAPI(q.config)
    return q


@pytest.fixture(scope="function")
def test_bot_and_queue(qalx):
    class TestBot(Bot):
        def __init__(self,*args, **kwargs):
            super(TestBot, self).__init__(*args, **kwargs)

        def get_context(self):
            return dict(

                Q_WAITTIMESECONDS=10,  # wait this long between attempts to get a message from the queue
                Q_MSGBATCHSIZE=1,  # number of messages to get in each request
                Q_WAITTIMEMAXSPREADING=12,  # the maximum wait time is this times the Q_WAITTIMESECONDS,
                SAVE_INTERMITTENT=True,  # save the entity between
                SKIP_FINAL_SAVE=False,  # don't save after post-processing
                KILL_AFTER=1,
                LOGGING_LEVEL=LOGGING_DEFAULTS['LEVEL'],  # What level we should log at by default
                LOGGING_CONFIG_PATH=LOGGING_DEFAULTS['CONFIG_PATH'], # The path to a custom logging dictConfig
                LOG_FILE_PATH=LOGGING_DEFAULTS['LOG_FILE_PATH']  # The path where log files will be stored
            )

        @property
        def config(self):
            conf = BotConfig(self.get_context())
            if not self.skip_ini:
                conf.from_inifile(self.bot_profile_name)
            conf.update(DEV_CONFIGS)
            return conf
    BOT_NAME = append_short_uuid("TEST_BOT")
    QUEUE_NAME = append_short_uuid("TEST_QUEUE")
    bot = TestBot(BOT_NAME, QUEUE_NAME, skip_ini=True)
    bot.user_qalx = qalx
    return bot, QUEUE_NAME


def test_add_item_data(qalx):
    item = qalx.add_item_data({"here_is": "some data"})
    assert item.get("guid")
    qalx.rest_api.delete(f"item/{item.get('guid')}")
    with pytest.raises(QalxAPIResponseError):
        qalx.get_entity_by_guid("item", item.get("guid"))


def test_item_file(qalx):
    _handle, path = mkstemp()
    os.close(_handle)
    random_string = ''.join([choice(printable+whitespace) for _ in range(1000)])
    with open(path, "w") as f:
        f.write(random_string)
    item = qalx.add_item_file(file_path=path)
    assert item.get("guid")
    archived_item = qalx.archive_entity_by_guid('item', item.get("guid"))
    assert archived_item['info']['archived']
    item_guid = item['guid']
    item_by_guid = qalx.get_entity_by_guid('item', item_guid)
    pass


def f_init(qalx):
    print('initialisation')
    return True


def f_begin(job):
    print('begin')
    job.add_step_result(True, {"test": "functional"})


def f_preload(job):
    print('preload')
    job.add_step_result(True, {"test": "functional"})


def f_onload(job):
    print('onload')
    job.entity['data']['onload'] = True
    job.add_step_result(True, {"test": "functional"})


def f_preprocess(job):
    print('preprocess')
    job.entity['data']['preprocess'] = True
    job.add_step_result(True, {"test": "functional"})


def f_process(job):
    how_long = job.entity['data']['how long?']
    sleep(how_long)
    guid = job.entity['guid']
    print(f'process takes {how_long}s on {guid[-6:]}')
    job.entity['data']['process'] = True
    job.add_step_result(True, {"test": "functional"})


def f_precompletion(job):
    print('precompletion')
    job.entity['data']['precompletion'] = True
    job.add_step_result(True, {"test": "functional"})


def f_postprocess(job):
    print('postprocess')
    job.entity['data']['postprocess'] = True
    job.add_step_result(True, {"test": "functional"})


def f_onwait(job):
    print('onwait')
    job.add_step_result(True, {"test": "functional"})


def f_ontermination(job):
    print('ontermination')
    job.add_step_result(True, {"test": "functional"})


def test_bot_items(qalx, test_bot_and_queue):
    test_bot, queue_name = test_bot_and_queue
    queue = qalx.add_queue(queue_name)
    items = []
    for n in range(10):
        item = qalx.add_item_data({"some_data_to_process": "some data",
                                   "how long?": randint(2, 10)})
        queue.submit_entity(item)
        items.append(item)

    test_bot.initialisation_function = f_init
    test_bot.begin_function = f_begin
    test_bot.preload_function = f_preload
    test_bot.onload_function = f_onload
    test_bot.preprocess_function = f_preprocess
    test_bot.process_function = f_process
    test_bot.precompletion_function = f_precompletion
    test_bot.postprocess_function = f_postprocess
    test_bot.onwait_function = f_onwait
    test_bot.ontermination_function = f_ontermination
    test_bot.start(2)
    life_cycle = ('onload',
                  'preprocess',
                  'process',
                  'precompletion',
                  'postprocess')

    for ui in items:
        updated_item = qalx.get_entity_by_guid('item', ui['guid'])
        for part in life_cycle:
            assert updated_item['data'].get(part)


def beam_calcs(job):
    beam_data_guid, weight_data_guid = job.entity['item_guids']  # unpack our input items
    beam_data = job.qalx.get_entity_by_guid('item', beam_data_guid)['data']
    weight_data = job.qalx.get_entity_by_guid('item', weight_data_guid)['data']

    # define a stress calculation function
    def stress_of_beam_in_bending(beam_length, beam_thickness, beam_weight):
        """calculates bending stress in a simply supported beam
        """
        beam_area = beam_length * beam_thickness
        beam_cog = beam_length / 2
        beam_moment = beam_weight * beam_cog
        return beam_moment / beam_area

    stress = stress_of_beam_in_bending(
        beam_data['length'],
        beam_data['thickness'],
        weight_data['value'])

    stress_item = job.qalx.add_item_data(data={
        "Stress": stress,
        "Spec code": beam_data['CODE']
    })
    job.entity['item_guids'].append(stress_item['guid'])
    job.save_entity()


def test_example_set(qalx,  test_bot_and_queue):
    test_bot, queue_name = test_bot_and_queue
    specs = [
        {"CODE": "B1", "thickness": 5, "length": 15},
        {"CODE": "B2", "thickness": 6, "length": 14},
        {"CODE": "B3", "thickness": 4, "length": 17},
    ]

    items = []
    for shape in specs:
        item = qalx.add_item_data(shape, meta={"shape_source": "beam-spec-123"})
        items.append(item)

    weight = {"value": 10, "units": "kg"}
    weight_item = qalx.add_item_data(weight)

    sets = []
    for item in items:
        set_ = qalx.add_set([item, weight_item])
        sets.append(set_)

    group = qalx.add_group(sets, meta={"batch": "Quickstart docs batch"})
    queue = qalx.get_or_create_queue(queue_name)
    queue.submit_sets_from_group(group)

    test_bot.process_function = beam_calcs
    test_bot.start(1)

    for s in sets:
        stressed_set = qalx.get_entity_by_guid('set', s['guid'])
        assert len(stressed_set['item_guids']) == 3  # will only work if the bot added the stress item
