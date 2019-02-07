from __future__ import print_function, absolute_import, unicode_literals
import os
import glob
import logging

from ilabs.client import ilabs_api, ilabs_datavault_api
from ilabs.client.ilabs_datavault_predictor import ILabsDatavaultPredictor
from ilabs.client.ilabs_bulk_predict import missing_files

def predict(input_filename, output_filename, collection, predictor):
    try:
        with open(input_filename, 'rb') as f:
            input_bytes = f.read()

        filename = os.path.basename(input_filename)

        output_bytes = predictor(input_bytes, collection, filename)
        with open(output_filename, 'wb') as f:
            f.write(output_bytes)

    except RuntimeError as e:
        return e

def _create_collection_if_needed(collection, api):
    present_collections = api.list_collections()
    if collection not in present_collections:
        api.create_collection(collection)
        policy = api.get_collection_policy(collection)
        policy['grants'] = {'api.innodatalabs.com': ['write']}
        api.set_collection_policy(collection, policy)
        print('Created an empty collection %s' % collection)

def bulk_predict(
    domain,
    input,
    output,
    collection,
    user_key=None,
    datavault_token=None,
    verbose=0
):
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    datavault_api = ilabs_datavault_api.ILabsDatavaultApi(user_key, datavault_token)
    _create_collection_if_needed(collection, datavault_api)

    api = ilabs_api.ILabsApi(user_key)
    predictor = ILabsDatavaultPredictor(api, datavault_api, domain)

    if os.path.isfile(input):
        if os.path.isdir(output):
            raise RuntimeError('When input is a single file, output is expected to be a file too. But its a directory: ' + output)
        elif os.path.isfile(output):
            print('Output file exists, nothing to do: ' + output)
            return

        error = predict(input, output, collection, predictor)
        print(os.path.basename(output), error or 'OK')

        return

    if not os.path.isdir(input):
        raise RuntimeError('Input file/directory does not exist: ' + input)

    if os.path.isfile(output):
        raise RuntimeError('When input is directory, output is expected to be a directory. But its a file: ' + output)

    if not os.path.exists(output):
        os.mkdir(output)
        print('Created output directory: ' + output)

    fileset = missing_files(input, output)
    if not fileset:
        return

    for fname in fileset:
        error = predict(
            os.path.join(input, fname),
            os.path.join(output, fname),
            collection,
            predictor
        )

        print(fname, error or 'OK')

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Sends all files from the input '
                    'directory to prediction service and '
                    'places result in the output directory')

    parser.add_argument('--domain', '-d', required=True, help='Prediction domain')
    parser.add_argument('--collection', '-c', required=True, help='Datavault collection name')
    parser.add_argument('--user_key', '-u', help='Secret user key')
    parser.add_argument('--datavault_token', '-t', help='Secret datavault token')

    parser.add_argument('input',
                        help='Input file or directory')
    parser.add_argument('output',
                        help='Output file or directory')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity. Use multiple times to get even more verbose')

    args = parser.parse_args()

    bulk_predict(**args.__dict__)

if __name__ == '__main__':
    main()
