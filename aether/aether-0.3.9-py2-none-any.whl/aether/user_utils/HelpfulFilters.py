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
        for ts_i in range(n_timestamps):
            spacecraft_id, sensor_id, collection = ae.contrib.logic.landsat.parse_sb_to_return_meta(builder, 0, qa_index)
            spacetime = ae.SpacetimeDynamic(builder, sky)
            qa_band = spacetime.bands(ts=ts_i, bands=qa_index)

            mask, labels = ae.contrib.logic.landsat.landsat_qa_band(qa_band, spacecraft_id, sensor_id, collection)
            label_indices = [i for i in range(len(labels)) if labels[i] in limits.keys()]

            if len(label_indices) == 0 or len(labels) == 0:
                continue

            mask = np.mean(mask, axis=(1,2))
            for i in label_indices:
                r = limits[labels[i]]
                keep_this_limit = HelpfulFilters._in_range(mask[0,i], r[0], r[1])
                action = "KEEPING" if keep_this_limit else "REMOVING"
                logger.info("{} timestamp {} for limit {}: value {}, range {}".format(
                    action, timestamps[ts_i], labels[i], mask[0,i], r))
                to_keep[ts_i] *= keep_this_limit
        return to_keep
