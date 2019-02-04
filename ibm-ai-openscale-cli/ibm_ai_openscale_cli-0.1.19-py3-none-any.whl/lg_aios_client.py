# coding=utf-8
import datetime
import time
import os
import logging
import pandas # for generating explain requests
import random
import json
from retry import retry
from ibm_ai_openscale_cli.aios_client import AIOSClient

logger = logging.getLogger(__name__)
parent_dir = os.path.dirname(__file__)

class AIOSClientLG(AIOSClient):

    @retry(tries=5, delay=4, backoff=2)
    def use_existing_subscription(self, ml_engine):
        self._subscriped_deployment_dict = {}
        deployment = ml_engine.get_existing_deployment()
        self._subscriped_deployment_dict['model_guid'] = deployment['model_guid']
        self._subscriped_deployment_dict['deployment_guid'] = deployment['deployment_guid']
        self._subscription = self.client.data_mart.subscriptions.get(self._subscriped_deployment_dict['model_guid'])

    @retry(tries=5, delay=1, backoff=2)
    def _generate_one_scoring_request(self, engine_client, score_input, deployment_url=None):
        start = datetime.datetime.now()
        if self._ml_engine_type == 'wml':
            predictions = engine_client.deployments.score(deployment_url, score_input)
        elif self._ml_engine_type == 'azureml':
            predictions = engine_client.score(self._subscription, score_input)
        end = datetime.datetime.now()
        return (start, end, predictions)

    def generate_scoring_requests(self, args, engine_client=None):
        if self._ml_engine_type == 'wml':
            engine_client = self.client.data_mart.bindings.get_native_engine_client(binding_uid=AIOSClient.binding_id)
            deployment_details = engine_client.deployments.get_details(self._subscriped_deployment_dict['deployment_guid'])
            deployment_url = engine_client.deployments.get_scoring_url(deployment_details)
            if self._is_icp and ':31002' not in deployment_url:
                deployment_url_host = ':'.join(deployment_url.split(':')[:2])
                args_url_host = ':'.join(self._target_env['aios_url'].split(':')[:2])
                deployment_url = deployment_url.replace('{}:16600'.format(deployment_url_host), '{}:31002'.format(args_url_host))
        elif self._ml_engine_type == 'azureml':
            deployment_url = None

        numscorerequests = args.lg_score_requests
        numscoresperrequest = args.lg_scores_per_request
        pause = args.lg_pause
        perfverbose = args.lg_verbose

        logger.info('Generate {} new scoring requests to AIOS'.format(numscorerequests))
        totalelapsed = 0
        firststart = datetime.datetime.now()
        lastend = firststart
        for _ in range(numscorerequests):
            score_input = self._model.get_score_input(numscoresperrequest)
            (start, end, predictions) = self._generate_one_scoring_request(engine_client, score_input, deployment_url)
            elapsed = end - start
            elapsed = (elapsed.days*24*3600 + elapsed.seconds) + elapsed.microseconds/1000000.0
            totalelapsed += elapsed
            lastend = end
            if perfverbose:
                logger.info('LG {}: request {} scores(s) in {:.3f} seconds, {} score(s) returned'.format(start, numscoresperrequest, elapsed, len(predictions['values'])))
            if pause > 0.0:
                time.sleep(pause)
        if numscorerequests > 0:
            duration = lastend - firststart
            duration = (duration.days*24*3600 + duration.seconds) + duration.microseconds/1000000.0
            logger.info('LG total score requests: {}, total scores: {}, duration: {:.3f} seconds'.format(numscorerequests, numscorerequests*numscoresperrequest, duration))
            logger.info('LG throughput: {:.3f} score requests per second, {:.3f} scores per second, average score request time: {:.3f} seconds'.format(numscorerequests/duration, numscorerequests*numscoresperrequest/duration, totalelapsed/numscorerequests))

    @retry(tries=5, delay=1, backoff=2)
    def _generate_one_explain(self, scoring_id):
        start = datetime.datetime.now()
        explain = self._subscription.explainability.run(scoring_id, background_mode=True)
        end = datetime.datetime.now()
        return (start, end, explain)

    @retry(tries=5, delay=4, backoff=2)
    def _get_available_scores(self, max_explain_candidates):
        start = datetime.datetime.now()
        payload_table = self._subscription.payload_logging.get_table_content(format='pandas', limit=max_explain_candidates)
        end = datetime.datetime.now()
        scoring_ids = []
        for index, row in payload_table.iterrows():
            scoring_ids.append(row['scoring_id'])
        random.shuffle(scoring_ids)
        return (start, end, scoring_ids)

    def generate_explain_requests(self, args):
        numexplainrequests = args.lg_explain_requests
        pause = args.lg_pause
        perfverbose = args.lg_verbose
        logger.info('Generate {} explain requests to AIOS'.format(numexplainrequests))
        if numexplainrequests < 1:
            return
        (start, end, scoring_ids) = self._get_available_scores(args.lg_max_explain_candidates)
        elapsed = end - start
        elapsed = (elapsed.days*24*3600 + elapsed.seconds) + elapsed.microseconds/1000000.0
        logger.info('Found {} available scores for explain, in {:.3f} seconds'.format(len(scoring_ids), elapsed))
        if numexplainrequests > len(scoring_ids):
            numexplainrequests = len(scoring_ids)

        if args.lg_explain_sync:
            input('Press ENTER to start generating explain requests')

        totalelapsed = 0
        firststart = datetime.datetime.now()
        lastend = firststart

        for i in range(numexplainrequests):
            scoring_id = scoring_ids[i]
            (start, end, explain) = self._generate_one_explain(scoring_id)
            elapsed = end - start
            elapsed = (elapsed.days*24*3600 + elapsed.seconds) + elapsed.microseconds/1000000.0
            totalelapsed += elapsed
            lastend = end
            if perfverbose:
                logger.info('LG {}: request explain in {:.3f} seconds {} {}'.format(start, elapsed, scoring_id, explain['metadata']['request_id']))
            if pause > 0.0:
                time.sleep(pause)

        duration = lastend - firststart
        duration = (duration.days*24*3600 + duration.seconds) + duration.microseconds/1000000.0
        logger.info('LG total explain requests: {}, duration: {:.3f} seconds'.format(numexplainrequests, duration))
        logger.info('LG throughput: {:.3f} explain requests per second, average explain request time: {:.3f} seconds'.format(numexplainrequests/duration, totalelapsed/numexplainrequests))

    @retry(tries=5, delay=4, backoff=2)
    def trigger_checks(self, args):
        if args.lg_checks:
            logger.info('Trigger immediate fairness check AIOS')
            self._subscription.fairness_monitoring.run()
            logger.info('Trigger immediate quality check AIOS')
            self._subscription.quality_monitoring.run()