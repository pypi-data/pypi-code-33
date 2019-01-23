import numpy as np
from aether.dataobjects.SpacetimeMixins import SpacetimeMixins
from aether.dataobjects.SpacetimeDynamic import SpacetimeDynamic
from aether.proto.api_pb2 import Spacetime as SpacetimePb
from aether.sky_utils import sky_utils
import rasterio
import json

################################################################################################################
#
# The Spacetime object is a 4-D numpy object with associated metadata and timestamps. It removes the geospatial
# aspects of the Spacetime object. However, it gains the ease and guarantees of being a 4-D numpy object, like data
# processing. It is intended to mirror all Spacetime functionality that does not include geospatial functions.
#
################################################################################################################


class Spacetime(object):

    def __init__(self, stack, timestamps, metadata, pb=None):
        self._stack, self._timestamps, self._metadata, self._pb = None, None, None, None
        self.update(stack, timestamps, metadata, pb=pb)

    def update(self, stack, timestamps=None, metadata=None, pb=None):
        if len(stack.shape) == 2:
            stack = np.expand_dims(np.expand_dims(stack, axis=0), axis=3)
        elif len(stack.shape) == 3:
            stack = np.expand_dims(stack, axis=3)

        self._stack = stack

        self._timestamps = timestamps if timestamps is not None else self._timestamps
        self._metadata = metadata if metadata is not None else self._metadata
        self._pb = pb if pb is not None else self._pb
        return self

    def timestamps(self):
        return self._timestamps

    def metadata(self):
        return self._metadata

    def as_numpy(self):
        return self._stack

    def bands(self, bands=None, ts=None):
        ts, bands = self._normalize_inputs(ts, bands)
        return self._stack[ts][:,:,:,bands]

    def _normalize_inputs(self, ts, bands):
        if bands is None:
            bands = range(self._stack.shape[3])
        if ts is None:
            ts = range(self._stack.shape[0])

        if isinstance(ts, int):
            ts = [ts]
        if isinstance(bands, int):
            bands = [bands]
        return ts, bands

    def _has_color_table(self):
        return True if self._generate_color_table() is not None else False

    def _generate_color_table(self):
        try:
            pb = self._pb
            if pb is not None:
                ct = json.loads(pb.color_table)
                return ct
        except:
            return None

    def _generate_mask(self):
        try:
            pb = self._pb
            if pb is not None:
                mask = np.frombuffer(sky_utils.deserialize_numpy(pb.numpy_mask_values), dtype=np.bool)
                mask = np.reshape(mask, newshape=self._stack.shape[1:3])
                return mask
        except:
            return None

    def generate_image(self, ts, bands, transparent=True, show_now=True, save_to=None):
        ts, bands = self._normalize_inputs(ts, bands)

        stack = self.bands(bands, ts)

        color_table = None
        if self._has_color_table():
            color_table = self._generate_color_table()
        mask = self._generate_mask() if transparent else None

        SpacetimeMixins.generate_image(stack, len(bands),
                                       mask=mask, color_table=color_table,
                                       show_now=show_now, save_to=save_to)

    @staticmethod
    def from_pb(s, app=None):
        if app is not None:
            return s.from_pb(s)

        stack = sky_utils.numpy_pb_to_arr(s.stack)

        timestamps = s.timestamps
        metadata = s.properties

        return Spacetime(stack, timestamps, metadata, pb=s)

    def to_pb(self, serialize_as_json=False):
        built = self._pb if self._pb is not None else SpacetimePb()

        stack = np.copy(self.as_numpy(), order='C')
        timestamps = self.timestamps()
        metadata = dict(self.metadata())

        built.timestamps.extend(timestamps)
        built.properties.update(metadata)
        sky_utils.numpy_arr_to_pb(stack, built.stack, as_json=serialize_as_json)

        return built


    @staticmethod
    def copy_builder_to_spacetime(builder, sky):
        spacetime = SpacetimeDynamic(builder, sky)
        data = spacetime.bands()
        timestamps = spacetime.timestamps()
        metadata = spacetime._metadata(None, None)

        s = SpacetimePb()
        s.polygon.CopyFrom(builder.polygon)
        s.timestamps.extend(timestamps)

        ref_src_f = spacetime.get_reference_crs()
        try:
            with rasterio.open(ref_src_f.name) as src:
                mask = src.read_masks(1)
                sky_utils.numpy_arr_to_pb(mask, s.mask, as_json=False)
        except:
            pass
        try:
            ct = spacetime._generate_color_table(0, 0)
            if ct is not None:
                s.color_table = json.dumps(ct)
        except:
            pass

        return Spacetime(data, timestamps, metadata, s)
