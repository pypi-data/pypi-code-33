import numpy as np
import aether as ae
from api.processes.SkyApplicationFrameworkResource import SkyFrameworkComponent
from sklearn.ensemble.forest import RandomForestClassifier

from aether.session.Exceptions import SkySDKRequestParserError, SkySDKRuntimeError
from aether.sky_utils import sky_utils

from flask_restful import reqparse

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MachineLearningApp(SkyFrameworkComponent):

    def __init__(self):
        super(MachineLearningApp, self).__init__()

    def availableMethods(self):
        return dict(
            Train="Train",
            Infer="Infer",
        )

    # def initialize(self):
    #     pass

    def parseRequest(self, method_name=None):
        method_args = None

        if method_name == "Train":
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('save_identifier', type=str, required=True, location='json')
            parser.add_argument('allow_overwrite', type=bool, required=False, default=False, location='json')
            parser.add_argument('model_reference', type=str, required=False, default="Sklearn.RandomForest", location='json')
            parser.add_argument('model_parameters', type=str, required=False, location='json')
            args = parser.parse_args()

            try:
                model_parameters = args.model_parameters
                if model_parameters is not None:
                    model_parameters = json.loads(model_parameters)
            except:
                raise SkySDKRuntimeError("Failed to load JSON model_parameters.")

            if args.model_reference is not "Sklearn.RandomForest":
                raise SkySDKRuntimeError("Only model_reference value as Sklearn.RandomForest supported at this time.")

            method_args = dict(
                save_identifier=args.save_identifier,
                allow_overwrite=args.allow_overwrite,
                model_reference=args.model_reference,
                model_parameters=model_parameters,

            )

        elif method_name == "Infer":
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('save_identifier', type=str, required=True, location='json')
            parser.add_argument('allow_overwrite', type=bool, required=False, default=False, location='json')
            args = parser.parse_args()

            method_args = dict(
                save_identifier=args.save_identifier,
                allow_overwrite=args.allow_overwrite,
            )

        if method_args is None:
            msg = "No argument parser provided for method_name {}".format(method_name)
            raise SkySDKRuntimeError(msg)

        return method_args

    def Train(self, method_args, uuid, builders):
        ae.GlobalConfig.set_user(uuid)
        with ae.SkySession() as sky:
            spacetime = sky.download(builders)
            spacetime = ae.Spacetime.from_pb(spacetime)



    #
    # indices = self._sample_indices_using_mask(spacetime, method_args)
    #         new_stack = spacetime.as_numpy()[:,indices[0], indices[1],:]
    #         new_stack = np.expand_dims(new_stack, axis=1) # To make a [n_ts, 1, n_samples, n_band] array.
    #
    #         try:
    #             metadata = json.loads(spacetime.metadata())
    #             src_metadata = json.loads(metadata["src_metadata"])
    #             src_metadata.update(dict(
    #                 width=new_stack.shape[2],
    #                 height=new_stack.shape[1],
    #             ))
    #             metadata["src_metadata"] = json.dumps(src_metadata)
    #             metadata = json.dumps(metadata)
    #         except:
    #             raise SkySDKRuntimeError("Spacetime missing src_metadata governing raster parameters")
    #
    #         spacetime = spacetime.update(new_stack, spacetime.timestamps(), metadata)
    #         builder = sky.upload(spacetime)
    #     return builder


    @staticmethod
    def train_on(classifier, data_x, data_y):
        s = data_x.shape
        n_pixels = s[0] * s[2] * s[3]
        data_x = np.reshape(np.transpose(data_x, axes=[0,2,3,1,4]), (n_pixels, s[1] * s[4]))


        if data_y.shape[4] != 1:
            print("ERROR: data_y shapes with multiple layers not yet supported. Everything will break.")
        data_y = np.reshape(data_y, (n_pixels))

        if self._model_config.down_sample_to is not None and int(self._model_config.down_sample_to) < n_pixels:
            subsample = np.random.randint(n_pixels, size=int(self._model_config.down_sample_to))
            data_x = data_x[subsample, :]
            data_y = data_y[subsample]

        self._ensemble.append(self._create_new_classifier().fit(data_x, data_y))



    def _create_new_classifier(self, method_args):
        model_parameters = dict(n_estimators=100, criterion="gini", max_features="auto",
                                max_depth=None, bootstrap=True, n_jobs=2, random_state=0,
                                verbose=0, warm_start=True)

        if method_args["model_parameters"] is not None:
            model_parameters = method_args["model_parameters"]

        return RandomForestClassifier(**model_parameters)