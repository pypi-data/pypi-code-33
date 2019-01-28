import aether as ae
import numpy as np
import json

import logging
logger = logging.getLogger(__name__)

class HelpfulFilters(object):

    @staticmethod
    def applyFilterResults(builder, to_keep):
        timestamps = list(sorted(builder.timestamps.keys()))
        for ts_i in range(len(to_keep)):
            if not to_keep[ts_i]:
                del builder.timestamps[timestamps[ts_i]]
        return builder

    @staticmethod
    def _in_range(d, the_min=None, the_max=None):
        keep = np.ones(dtype=np.bool, shape=d.shape)
        if the_max is not None:
            keep *= (d <= the_max)
        if the_min is not None:
            keep *= (d >= the_min)
        return keep

    @staticmethod
    def LandSatCloudFilter(sky, builder, limits, qa_index, polygon=None):
        timestamps = list(sorted(builder.timestamps.keys()))
        n_timestamps = len(timestamps)
        to_keep = [True] * n_timestamps

        if len(limits) == 0:
            return to_keep

        # Copying builder to alter polygon if necessary.
        # This ensures only QA bands are cropped.
        if polygon is not None:
            new_builder = ae.SpacetimeBuilder()
            new_builder.CopyFrom(builder)
            builder = new_builder
            builder.polygon.latlngs = json.dumps(polygon.to_latlngs())
            for timestamp in timestamps:
                # This iteration is dynamic, so must delete from the array in reverse order.
                for b_i in range(len(builder.timestamps[timestamp].layers)-1, -1, -1):
                    if b_i != qa_index:
                        del builder.timestamps[timestamp].layers[b_i]
            builder = sky.crop(builder)
            qa_index = 0

        # Need to do one at a time in case spacecraft_id, etc, change
        masks, labels = ae.contrib.satellite.LandSatMasks(builder, sky, qa_index)
        masks = np.mean(masks, axis=(1,2))
        for ts_i in range(n_timestamps):
            label_indices = [i for i in range(len(labels)) if labels[i] in limits.keys()]

            if len(label_indices) == 0 or len(labels) == 0:
                continue

            for i in label_indices:
                r = limits[labels[i]]
                keep_this_limit = HelpfulFilters._in_range(masks[ts_i, i], r[0], r[1])
                action = "KEEPING" if keep_this_limit else "REMOVING"
                logger.info("{} timestamp {} for limit {}: value {}, range {}".format(
                    action, timestamps[ts_i], labels[i], masks[ts_i,i], r))
                to_keep[ts_i] *= keep_this_limit
        return to_keep
