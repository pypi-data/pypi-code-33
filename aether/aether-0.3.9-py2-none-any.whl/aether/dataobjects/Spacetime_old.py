import base64

import numpy as np
from PIL import Image
import json

# from aether.proto.api_pb2 import Spacetime as Spacetime_pb
from aether.sky_utils import sky_utils

class BoundMethod():

    def __init__(self):
        pass

    def if_placeholder(self):
        pass

    def method(self):
        pass

class Spacetime(object):

    def __init__(self, stack, timestamps, metadata):
        self._stack = stack if len(stack.shape) == 4 else np.expand_dims(stack, axis=3)
        self._timestamps = timestamps
        self._metadata = metadata

    def update(self, stack, timestamps, metadata):
        self._stack = stack if len(stack.shape) == 4 else np.expand_dims(stack, axis=3)
        self._timestamps = timestamps
        self._metadata = metadata
        return self

    def timestamps(self):
        return self._timestamps

    def metadata(self):
        return self._metadata

    def as_numpy(self):
        return self._stack

    def band(self, b):
        return self._stack[:,:,:,b]

    def _has_color_table(self):
        return True if self._generate_color_table() is not None else False

    def _generate_color_table(self):
        try:
            table = json.loads(json.loads(self.metadata())["colormap"])
            return table
        except:
            return None

    def generate_mask(self):
        try:
            mask = np.array(json.loads(json.loads(self.metadata())["src_mask"]))
            return mask
        except:
            return None

    def generate_image(self, ts, bands, transparent=True, show_now=True, save_to=None):
        if isinstance(ts, str):
            if ts not in self._timestamps:
                print("Timestamp {} not found in Spacetime with timestamps {}".format(ts, self._timestamps))
                return
            ts = self._timestamps.index(ts)
        for b in bands:
            if b > self._stack.shape[3] - 1:
                print("Band Index {} out of range.".format(b))
                return

        # Are we working with a color table?
        if len(bands) == 1 and self._has_color_table():
            d = np.array(self._stack[ts][:,:,bands], dtype=int)
            ct = self._generate_color_table()
            lookup = np.zeros(shape=(max([int(x) for x in ct.keys()]) + 1, 4))
            for k in ct.keys():
                lookup[int(k)] = ct[k]
            d = lookup[d]
            mode = "RGBA"
            image = Image.fromarray(np.array(d, dtype=np.uint8), mode=mode)

        else:
            # Else, normalizes to 0 to 1.
            d = np.array(self._stack[ts][:,:,bands], dtype=np.float)
            v_min, v_max = np.nanmin(d), np.nanmax(d)
            r = 1.0 if v_max == v_min else v_max - v_min
            d -= v_min
            d *= 255.0 / float(r)
            mode = "RGB" if len(bands) == 3 else "L"
            d = d if len(bands) == 3 else np.squeeze(d, axis=-1)
            image = Image.fromarray(np.array(d, dtype=np.uint8), mode=mode)

        if transparent and (self.generate_mask() is not None):
            mask = np.clip(self.generate_mask() * 255, None, 255)
            mask = Image.fromarray(np.array(mask, dtype=np.uint8), mode="L")
            image.putalpha(mask)

        if show_now:
            image.show()
        if save_to is not None:
            image.save(save_to)


    def generate_chart(self, bands, show_now=True, save_to=None, subsample_to=None):
        pass

    @staticmethod
    def from_pb(s, app=None):
        if app is not None:
            return s.from_pb(s)

        shape = np.array(s.array_shape)
        stack = np.frombuffer(sky_utils.deserialize_numpy(s.array_values), dtype=np.float)
        stack = np.reshape(stack, newshape=shape)
        timestamps = s.timestamps
        metadata = s.metadata
        return Spacetime(stack, timestamps, metadata)

    def to_pb(self):
        s = Spacetime_pb()
        s.timestamps.extend(self.timestamps())
        s.metadata = str(self._metadata)
        s.array_shape.extend(list(self.as_numpy().shape))
        s.array_values = base64.b64encode(self.as_numpy())
        return s