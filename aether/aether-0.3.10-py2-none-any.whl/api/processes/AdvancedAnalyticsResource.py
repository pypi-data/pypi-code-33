import aether as ae
from aether.proto.api_pb2 import SpacetimeBuilder
from aether.dataobjects.Spacetime import Spacetime as SpacetimeDo
from flask_restful import reqparse
import json
from skimage.segmentation import felzenszwalb
from skimage.segmentation import mark_boundaries
from scipy.ndimage import gaussian_filter
import numpy as np
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from api.base.PostMethodResourceBase import PostMethodResourceBase

import logging
logger = logging.getLogger(__name__)

class AdvancedAnalyticsResource(PostMethodResourceBase):

    _post_methods = dict(
        VideoSegmentation="VideoSegmentation",
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects
        super(AdvancedAnalyticsResource, self).__init__(global_objects, logger)

    def VideoSegmentation(self, request):
        """Applies a Filter Function to a SpacetimeBuilder"""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('builder', type=str, required=True, location='json')
        parser.add_argument('function_args', type=str, required=True, location='json')
        args = parser.parse_args()

        builder = firebase_utils.verify_pb(args["builder"], SpacetimeBuilder(), return_pb_if_valid=True)
        if builder is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed builder object for builder_type.", 400, request, logger)

        try:
            filter_args = json.loads(args["filters_args"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly json'd filters args.", 401, request, self._logger, exc_info=True)

        try:
            # TODO(astrorobotic): This should *absolutely not* be attributed to the UUID. It should be admin.
            uuid = args["uuid"]
            ae.GlobalConfig.set_user(uuid)
            with ae.SkySession() as sky:
                spacetime = SpacetimeDo.copy_builder_to_spacetime(builder, sky)
            response, code = self._deterministic_image_segmentation(spacetime.bands())
            return api_utils.log_and_return_status(response, code, request, logger)
        except Exception:
            return api_utils.log_and_return_status("VideoSegmentation failed.".format(request), 500, request, logger, exc_info=True)

    def _deterministic_image_segmentation(self, stack):
        # This moves all timeseries into the bands axis, creating an {n_x, n_y, n_b * n_ts] matrix
        stack = np.transpose(stack, axes=[1,2,3,0])
        s = stack.shape
        stack = np.reshape(stack, newshape=(s[0], s[1], s[2]*s[3]))

        # This applies a 1 pixel Gaussian Filter.
        stack = np.stack([gaussian_filter(stack[:,:,i], sigma=1) for i in range(stack.shape[2])])
        stack = np.transpose(stack, axes=[1,2,0])

        # This super-samples the images. That can help draw boundaries clearer (though changes scales)
        fact = 1
        # fact = 3
        # stack = stack.repeat(fact, axis=0).repeat(fact, axis=1)

        segments = felzenszwalb(stack, scale=200, sigma=0.1, min_size=100 * fact**2)
        logger.info("Felzenszwalb number of segments: {}".format(len(np.unique(segments))))

        # This calculates the RMS of the segments. In theory, the RMS within a segment should be low.
        n_segments = len(np.unique(segments))
        s = stack.shape
        in_img = np.reshape(stack, newshape=(s[0]*s[1], s[2]))
        segments = np.reshape(segments, newshape=(s[0]*s[1]))
        rms = [np.sqrt(np.sum(np.square(np.nanstd(in_img[(segments == i)], axis=0)))) for i in range(n_segments)]
        rms = [r for r in rms if not np.isnan(r)]
        logger.info("The RMS of each segment: {}".format(rms))
        logger.info("This many segments have NaN RMS: {}".format(len(rms) - len(segments)))

        quality_value = np.std(rms)
        boundaries_image = mark_boundaries(np.zeros(stack.shape[0:2]), segments, mode="inner")
        response = dict(
            segments_mask=segments,
            boundaries_mask=boundaries_image,
            quality_value=quality_value,
        )
        return json.dumps(response), 200