import json
from multiprocessing import Manager

import pytest

from pyqalx import Bot
from tests.model_entities import queue_response, entities_response, bot_post


def bot_processes(bot, jobs, expected_output):
    """
    Helper function for handling the bot processes
    :param bot: The bot instance
    :param jobs: An instance of Manager().list().  Used to keep track of all
                 the jobs across multiple processes
    :param expected_output: An instance of Manager().list().  Used to keep
                            track of all outputs for the jobs across multiple
                            processes
    :return: bot, jobs, expected_output
    """
    @bot.initialisation
    def _initialisation(user_qalx):
        jobs.append('init_complete')
        return True

    @bot.begin
    def _begin(_job):
        val = "begin"
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.preload
    def _preload(_job):
        val = 'preload'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.onload
    def _onload(_job):
        val = 'onload'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.preprocess
    def _preprocess(_job):
        val = 'preprocess'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.process
    def _process(_job):
        val = 'process'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.precompletion
    def _precompletion(_job):
        val = 'precompletion'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.postprocess
    def _postprocess(_job):
        val = 'postprocess'
        _job.add_step_result(True, {"test": val})
        _job.stop = True
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.ontermination
    def _ontermination(_job):
        val = 'termination'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)

    @bot.onwait
    def _onwait(_job):
        val = 'onwait'
        _job.add_step_result(True, {"test": val})
        jobs.append(_job.last_step_result)
        expected_output.append(val)
    return bot, jobs, expected_output

@pytest.mark.xfail
def test_bot_runs_all_functions(mocker, qalx_class):
    """
    Tests that a bot runs through all the expected functions and processes
    them accordingly
    """
    # No response from status update
    status_update = {}
    get_queues = {
        'data': [queue_response],
    }

    get_item = entities_response['item'][0]
    mocked_api_request = mocker.patch(
        'pyqalx.core.qalx.Qalx._process_api_request')
    mocked_api_request.side_effect = [
        # The first call creates a bot
        bot_post,
        status_update,
        get_queues,
        queue_response,
        entities_response['item'][0],
    ]
    mocked_boto3 = mocker.patch('pyqalx.core.queue.boto3')
    mocked_boto3.client.return_value.receive_message.side_effect = [
        {'Messages': [{'Body': json.dumps({
            'entity_type': 'item',
            'entity_guid': get_item['guid']
        }),
            'ReceiptHandle': 'receipt handle'}]}
    ]
    bot = Bot(bot_name='test_bot',
              queue_name='test_queue',
              skip_ini=True,
              qalx_class=qalx_class)

    with Manager() as manager:
        # Use a manager for a shared state across all processes
        jobs = manager.list()
        expected_output = manager.list()

        bot, jobs, expected_output = bot_processes(bot, jobs, expected_output)

        bot.start(processes=1)
        assert jobs[0] == 'init_complete'

        for cnt, job in enumerate(jobs[1:]):
            assert job.result_data == {'test': expected_output[cnt]}
            # This test case should never wait
            assert job.result_data != {'test': 'onwait'}, \
                "BotProcess called `onwait` function when it shouldn't have"

@pytest.mark.xfail
@pytest.mark.slow
def test_bot_runs_all_functions_wait_response(mocker, qalx_class):
    """
    Tests that a bot runs through all the expected functions and processes
    them accordingly.  This also tests that the wait response works in case
    we don't get a message from SQS.
    This will take a while to complete due to the
    `sleep(wait_time * spread_factor)`
    """
    # No response from status update
    status_update = {}
    get_queues = {
        'data': [queue_response],
    }

    get_item = entities_response['item'][0]
    mocked_api_request = mocker.patch(
        'pyqalx.core.qalx.Qalx._process_api_request')
    mocked_api_request.side_effect = [
        # The first call creates a bot
        bot_post,
        status_update,
        get_queues,
        queue_response,
        entities_response['item'][0],
    ]
    mocked_boto3 = mocker.patch('pyqalx.core.queue.boto3')
    mocked_boto3.client.return_value.receive_message.side_effect = [
        {},
        {'Messages': [{'Body': json.dumps({
            'entity_type': 'item',
            'entity_guid': get_item['guid']
        }),
            'ReceiptHandle': 'receipt handle'}]}
    ]

    bot = Bot(bot_name='test_bot',
              queue_name='test_queue',
              skip_ini=True,
              qalx_class=qalx_class)

    with Manager() as manager:
        # Use a manager for a shared state across all processes
        jobs = manager.list()
        expected_output = manager.list()

        bot, jobs, expected_output = bot_processes(bot, jobs, expected_output)

        bot.start(processes=1)
        assert jobs[0] == 'init_complete'

        for cnt, job in enumerate(jobs[1:]):
            assert job.result_data == {'test': expected_output[cnt]}


@pytest.mark.slow
@pytest.mark.xfail
def test_bot_runs_all_functions_kill_after(mocker,
                                           qalx_class):
    """
    Tests that a bot runs through all the expected functions and processes
    them accordingly - killing the process if we have attempted to get messages
    more than `KILL_AFTER` times.  This also tests reading from the ini file.
    This will take a while to complete due to the
    `sleep(wait_time * spread_factor)`
    """
    # No response from status update
    status_update = {}
    get_queues = {
        'data': [queue_response],
    }

    get_item = entities_response['item'][0]
    mocked_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')  # noqa
    mocked_api_request.side_effect = [
        # The first call creates a bot
        bot_post,
        status_update,
        get_queues,
        queue_response,
        entities_response['item'][0],
    ]
    mocked_boto3 = mocker.patch('pyqalx.core.queue.boto3')
    mocked_boto3.client.return_value.receive_message.side_effect = [
        # This is key to the `KILL_AFTER` test.  We will kill after two
        # attempts.  Meaning that the actual message will never get read
        {},
        {},
        # This will never get read
        {'Messages': [{'Body': json.dumps({
            'entity_type': 'item',
            'entity_guid': get_item['guid']
        }),
            'ReceiptHandle': 'receipt handle'}]}
    ]
    # Mock the config file that is normally stored on the filesystem
    mocked_path = mocker.patch('pyqalx.config.os.path.exists')
    mocked_path.return_value = True
    mo = mocker.mock_open(read_data="[default]\nKILL_AFTER=2")
    mocker.patch('pyqalx.config.open', mo)

    bot = Bot(bot_name='test_bot',
              queue_name='test_queue',
              skip_ini=False,
              qalx_class=qalx_class)

    with Manager() as manager:
        # Use a manager for a shared state across all processes
        jobs = manager.list()
        expected_output = manager.list()

        bot, jobs, expected_output = bot_processes(bot, jobs, expected_output)

        bot.start(processes=1)
        assert jobs[0] == 'init_complete'

        for cnt, job in enumerate(jobs[1:]):
            assert job.result_data == {'test': expected_output[cnt]}
            for func_not_run in ['preload', 'onload', 'preprocess',
                                 'process', 'precompletion',
                                 'postprocess']:
                # None of these functions should have been called because we
                # killed the process before they were called
                assert job.result_data != {'test': func_not_run}, \
                    "%s function ran when it shouldn't have" % func_not_run
