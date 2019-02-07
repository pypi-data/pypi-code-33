import os
import time
import json
import logging


def noop(*av, **kav): pass

class ILabsDatavaultPredictor:

    def __init__(self, api, datavault_api, domain):
        self.api = api
        self.datavault_api = datavault_api
        self._domain = domain

    def __call__(self, binary_data, collection, filename, input_facet='master',
                    output_facet='prediction', progress=None):

        if progress is None:
            progress = noop

        progress('Uploading document %s in %s/%s' % (filename, collection, input_facet))
        out = self.datavault_api.upload(binary_data, collection, filename, facet=input_facet)
        response = self.api.predict_from_datavault(self._domain, collection, filename,
            input_facet=input_facet, output_facet=output_facet)

        task_id = response['task_id']
        task_cancel_url = response['task_cancel_url']
        document_output_url = response['document_output_url']
        task_status_url = response['task_status_url']
        output_filename = response['output_filename']
        progress('Job submitted, task id: %s' % task_id)

        try:
            count = 1
            for _ in range(100):
                for count_idx in reversed(range(count)):
                    time.sleep(1.0)
                    progress('retrying in: %s' % (count_idx+1))

                logging.info('Requesting status at %s', task_status_url)
                response = self.api.get(task_status_url)
                out = json.loads(response.decode())
                assert out is not None, response
                progress('progress: %s/%s' % (out['progress'], out['steps']))
                if out['completed']:
                    break
                count = min(count*2, 60)
            else:
                raise RuntimeError('timeout')

            task_cancel_url = None
        finally:
            if task_cancel_url is not None:
                logging.info('Cancelling job at %s', task_cancel_url)
                self.api.get(task_cancel_url)

        err = out.get('error')
        if err is not None:
            raise RuntimeError('Prediction server returned error: ' + err)

        progress('Fetching result')
        progress('Downloading document %s from %s/%s' % (filename, collection, output_facet))
        prediction = self.datavault_api.download(collection, filename, facet=output_facet)
        progress('Downloaded %s bytes' % len(prediction))

        return prediction

    def upload_feedback(self, binary_data, collection, filename, facet='feedback'):
        out = self.datavault_api.upload(binary_data, collection, filename, facet=facet)
