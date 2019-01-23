import numpy as np
import aether as ae
from api.processes.SkyApplicationFrameworkResource import SkyFrameworkComponent

from aether.session.Exceptions import SkySDKRequestParserError, SkySDKRuntimeError
from aether.sky_utils import sky_utils

from flask_restful import reqparse

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeoTiffSampleApp(SkyFrameworkComponent):

    def __init__(self):
        super(GeoTiffSampleApp, self).__init__()

    def availableMethods(self):
        return dict(
            Sample="Sample",
        )

    # def initialize(self):
    #     pass

    def parseRequest(self, method_name=None):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('mask', type=str, required=False, default=None, location='json')
        parser.add_argument('is_boolean', type=bool, required=True, location='json')
        parser.add_argument('n_samples', type=float, required=True, location='json')
        args = parser.parse_args()

        mask = args.mask
        if mask is not None:
            try:
                np_type = np.bool if args.is_boolean else np.float
                mask = np.frombuffer(sky_utils.deserialize_numpy(args.mask), dtype=np_type)
            except:
                raise SkySDKRequestParserError("Request contains mask that did not deserialize into a numpy array.")

        method_args = dict(
            mask=mask,
            is_boolean=args.is_boolean,
            n_samples=args.n_samples
        )

        return method_args

    @staticmethod
    def _sample_indices_using_mask(spacetime, method_args):
        n_samples = method_args["n_samples"]
        is_boolean = method_args["is_boolean"]
        mask = method_args["mask"]

        if not is_boolean:
            raise SkySDKRuntimeError("Non-Boolean masks (is_boolean=False) are not supported at this time.")

        shape = spacetime.as_numpy().shape

        try:
            if n_samples >= 0.0 and n_samples <= 1.0:
                n_samples = int(np.ceil(n_samples * shape[1] * shape[2]))
            else:
                n_samples = int(n_samples)
        except:
            msg = "n_samples value must be either an integer or a fraction between zero and one: {}".format(n_samples)
            raise SkySDKRuntimeError(msg)

        if mask is not None:
            if shape[1:3] != mask.shape:
                msg = "Mask shape ({}) and Spacetime shape ({}) must be equivalent in spatial dimension.".format(mask.shape, shape[1:3])
                raise SkySDKRuntimeError(msg)

            # Sample from a Boolean Mask (True is valid choice)
            choices = map(list, zip(*np.where(mask)))
            indices = [choices[r] for r in np.random.randint(0, high=len(choices), size=n_samples)]
            indices = np.array(map(list, zip(*indices)))
            logger.info("Mask has {} True values out of {} total. {} selected".format(np.sum(mask), mask.size, n_samples))
        else:
            indices = np.array([
                np.random.randint(0, high=shape[1], size=n_samples),
                np.random.randint(0, high=shape[2], size=n_samples),
                    ])
        return indices


    def Sample(self, method_args, uuid, builders):
        ae.GlobalConfig.set_user(uuid)
        with ae.SkySession() as sky:
            spacetimes = [sky.download(builder) for builder in builders]
            spacetimes = [ae.Spacetime.from_pb(spacetime) for spacetime in spacetimes]

            # Check that all spacetime objects are the same size.
            

            indices = self._sample_indices_using_mask(spacetime, method_args)
            new_stack = spacetime.as_numpy()[:,indices[0], indices[1],:]
            new_stack = np.expand_dims(new_stack, axis=1) # To make a [n_ts, 1, n_samples, n_band] array.

            try:
                metadata = json.loads(spacetime.metadata())
                src_metadata = json.loads(metadata["src_metadata"])
                src_metadata.update(dict(
                    width=new_stack.shape[2],
                    height=new_stack.shape[1],
                ))
                metadata["src_metadata"] = json.dumps(src_metadata)
                metadata = json.dumps(metadata)
            except:
                raise SkySDKRuntimeError("Spacetime missing src_metadata governing raster parameters")

            spacetime = spacetime.update(new_stack, spacetime.timestamps(), metadata)
            builder = sky.upload(spacetime)
        return builder

