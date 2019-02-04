import datetime

from copy import deepcopy
from multiprocessing import Process
from time import sleep
from typing import NamedTuple

import sys

from pyqalx import Qalx
from pyqalx.config import BotConfig
from pyqalx.core.errors import QalxBotInitialisationFailed

# We may need below, we may not. What can I say? Dill waters run deep.
# from pyqalx.vendor import dill
# dill.settings['recurse'] = True
from pyqalx.core.log import LOGGING_DEFAULTS


def do_nowt(*args, **kwargs):
    pass


def do_nowt_right(*args, **kwargs):
    return True


class QalxJob:
    __slots__ = ('qalx', 'entity', 'stop',
                 '_current_step', '_process', '_bot_entity', '_queue_message', '_step_results')

    def __init__(self, bot_process):
        """a Job to process

        :param bot_process:
        :type bot_process BotProcess:
        """
        self._process = bot_process
        self.qalx = bot_process.qalx
        self.stop = False
        self._step_results = []
        self._bot_entity = bot_process.api_entity

    def publish_status(self, status_string="", status_dict=None):
        """update the status of the bot

        :param status_string: short message about the bot status
        :type status_string: str
        :param status_dict: structured status data
        """
        status = {
            'time': datetime.datetime.now().isoformat(),
            'message': status_string
        }
        if status_dict is not None:
            status.update(status_dict)
        self.qalx.update_bot_status(self._bot_entity['guid'], status)

    def add_step_result(self, success=True, result_data=None):
        """indicate success and add info about the current step

        :param success: was the step successful or not
        :type success: bool
        :param result_data: data from the result
        :type result_data: dict
        """
        self._step_results.append(StepResult(success=success, step_name=self._current_step, result_data=result_data))

    @property
    def last_step_result(self):
        if self._step_results:
            return self._step_results[-1]
        else:
            return None

    def save_entity(self):
        """save the entity in the message"""
        self.qalx.save_entity(self.entity)


class StepResult(NamedTuple):
    step_name: str = ""
    success: bool = False
    result_data: dict = {}


class BaseBot:

    def __init__(self):
        super().__init__()

    def get_context(self):
        return dict(
            Q_WAITTIMESECONDS=10,  # wait this long between attempts to get a message from the queue
            Q_MSGBATCHSIZE=1,  # number of messages to get in each request
            Q_WAITTIMEMAXSPREADING=12,  # the maximum wait time is this times the Q_WAITTIMESECONDS,
            SAVE_INTERMITTENT=False,  # save the entity between
            SKIP_FINAL_SAVE=False,  # don't save after post-processing
            KILL_AFTER=None,
            LOGGING_LEVEL=LOGGING_DEFAULTS['LEVEL'],  # What level we should log at by default
            LOGGING_CONFIG_PATH=LOGGING_DEFAULTS['CONFIG_PATH'],  # The path to a custom logging dictConfig
            LOG_FILE_PATH=LOGGING_DEFAULTS['LOG_FILE_PATH']  # The path where log files will be stored
        )


class Bot(BaseBot):

    def __init__(self, bot_name, queue_name, user_profile="default", bot_profile_name="default", skip_ini=False,
                 **kwargs):
        super(Bot, self).__init__()
        self.bot_name = bot_name
        self.queue_name = queue_name
        self.kwargs = kwargs
        self.bot_profile_name = bot_profile_name
        self.skip_ini = skip_ini
        self.user_qalx = Qalx(user_profile, skip_ini=skip_ini)

        # bot lifecycle functions
        self.initialisation_function = do_nowt_right
        self.begin_function = do_nowt
        self.preload_function = do_nowt
        self.onload_function = do_nowt
        self.preprocess_function = do_nowt
        self.process_function = do_nowt
        self.precompletion_function = do_nowt
        self.postprocess_function = do_nowt
        self.onwait_function = do_nowt
        self.ontermination_function = do_nowt

    def _collect_steps(self):
        steps = {}
        for fn in self.__dir__():
            if fn.endswith("_function"):
                steps[fn] = getattr(self, fn)  # serialise functions
                # steps[fn] = dill.dumps(getattr(self, fn))  # serialise functions
        return steps

    def start(self, processes=1):
        if self.initialisation_function:
            init_result = self.initialisation_function(self.user_qalx)
            if not init_result:
                raise QalxBotInitialisationFailed("The initialisation function returned a False-like value.")
        steps = self._collect_steps()
        processors = [
            BotProcess(self.config, steps, self.user_qalx, self.queue_name, self.skip_ini, **self.kwargs) for _ in
            range(processes)
        ]
        [
            p.start() for p in processors
        ]
        [
            p.join() for p in processors
        ]

    def initialisation(self, func):
        """decorator to to register the initialisation

        `initialisation` is executed with no argument
        :param func: function to be executed
        :return:
        """
        self.initialisation_function = deepcopy(func)

    def begin(self, func):
        """decorator to to register the begin

        `begin` is executed with no argument
        :param func: function to be executed
        :return:
        """
        self.begin_function = func

    def preload(self, func):
        """decorator executed before entity is loaded from qalx.

        `preload` is executed with a single qalx.QueueMessage argument.
        :param func: function to be executed
        :return:
        """
        self.preload_function = func

    def onload(self, func):
        """decorator to register the onload

        :param func: function to be executed
        :return:
        """
        self.onload_function = func

    def preprocess(self, func):
        """decorator to register preprocess function

        :param func: function to register
        :return:
        """
        self.preprocess_function = func

    def process(self, func):
        """decorator to register process function

        :param func: function to register
        :return:
        """
        self.process_function = func

    def precompletion(self, func):
        """decorator to register precompletion function

        :param func: function to register
        :return:
        """
        self.precompletion_function = func

    def postprocess(self, func):
        """decorator to register postprocess function

        :param func: function to register
        :return:
        """
        self.postprocess_function = func

    def onwait(self, func):
        """decorator to register onwait function

        :param func: function to register
        :return:
        """
        self.onwait_function = func

    def ontermination(self, func):
        """decorator to register ontermination function

        :param func: function to register
        :return:
        """
        self.ontermination_function = func

    @property
    def config(self):
        conf = BotConfig(self.get_context())
        if not self.skip_ini:
            conf.from_inifile(self.bot_profile_name)
        return conf


class BotProcess(Process):

    def __init__(self, config, steps, user_qalx, queue_name, skip_ini, **kwargs):
        super(BotProcess, self).__init__()
        self.config = config
        self.skip_ini = skip_ini
        self.steps = steps

        # at one point in time we got pickle errors - if we get them again then we might need dill as below:
        # self.steps = {}
        # for f_name, f_dill in steps.items(): # de-serialise functions
        #     self.steps[f_name] = dill.loads(f_dill)

        self.queue_name = queue_name
        if "qalx_class" in kwargs:  # to allow testing with various other configs
            qalx_class = kwargs['qalx_class']
            kwargs.pop('qalx_class')
        else:
            qalx_class = Qalx

        self.kwargs = kwargs
        self.api_entity = user_qalx.add_bot(self.config, meta=kwargs)
        self.config['TOKEN'] = self.api_entity['info']['credentials']['token']
        self.qalx = qalx_class(bot_config=self.config, skip_ini=self.skip_ini)
        self.job = QalxJob(self)

    def _check_alive(self):
        if self.job.stop:
            self.steps['ontermination_function'](self.job)
            sys.exit()

    def _run_functions(self):
        self.job.publish_status("running")
        if self.steps['begin_function']:
            self.job._current_step = "Begin"
            self.steps['begin_function'](self.job)
            self._check_alive()

        # get queue
        self.queue = self.qalx.get_queue_by_name(self.queue_name)
        time_to_wait = int(self.config['Q_WAITTIMESECONDS'])
        max_spreading = int(self.config['Q_WAITTIMEMAXSPREADING'])
        kill_after = self.config['KILL_AFTER']
        spread_factor = 1
        no_message_attempts = 0
        while not self.job.stop:
            q_msgs = self.qalx.get_queue_messages(self.queue)
            if q_msgs:
                spread_factor = 1
                for q_msg in q_msgs:
                    self.job._queue_message = q_msg
                    self._process_functions()
                #TODO: I don't think this does anything?
                no_message_attempts = 0
            else:
                self.job._queue_message = None
                self.job._current_step = 'OnWait'
                if self.steps['onwait_function'] is not None:
                    self.steps['onwait_function'](self.job)
                    self._check_alive()
                no_message_attempts += 1

                sleep(time_to_wait * spread_factor)
                next_spread = spread_factor + 1
                spread_factor = min(max_spreading, next_spread)  # never spread beyond a max factor
            if (kill_after is not None) and (no_message_attempts >= int(kill_after)):
                # TODO: I think we need to set self.job._current_step = 'OnTerminate' here??
                self.job.stop = True
                self._check_alive()

    def _process_functions(self):
        def process_as_far_as_possible(functions):
            for fn, step_name in functions:
                if not self.job.stop and fn:
                    self.job._current_step = step_name
                    fn(self.job)
                    self._check_alive()
                    if self.config.getboolean('SAVE_INTERMITTENT'):
                        self.job.save_entity()
                else:
                    break
            if not self.config.getboolean('SKIP_FINAL_SAVE'):
                self.job.save_entity()
            return self.job

        # PreLoad
        if self.steps['preload_function']:
            self.job._current_step = 'PreLoad'
            self.steps['preload_function'](self.job)
            self._check_alive()

        # Process steps
        process_functions = [
            (self.steps['onload_function'], 'OnLoad'),
            (self.steps['preprocess_function'], 'PreProcess'),
            (self.steps['process_function'], 'Process'),
            (self.steps['precompletion_function'], 'PreCompletion'),
            (self.steps['postprocess_function'], 'PostProcess')
        ]
        if not self.job.stop:
            entity_type = self.job._queue_message.body['entity_type']
            entity_guid = self.job._queue_message.body['entity_guid']
            self.job.entity = self.qalx.get_entity_by_guid(entity_type, entity_guid)
            self.queue.delete_message(self.job._queue_message)  # TODO: build in a heartbeat
            process_as_far_as_possible(process_functions)

    def run(self):
        self._run_functions()
