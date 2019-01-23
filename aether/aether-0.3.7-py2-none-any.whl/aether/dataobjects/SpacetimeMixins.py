import numpy as np
from PIL import Image

################################################################################################################
#
# The SpacetimeMixins are function helpers and operators that can be used on either Spacetime or SpacetimeLite
# object.
#
################################################################################################################


class SpacetimeMixins(object):

    @staticmethod
    def generate_image(stack, n_bands, mask=None, color_table=None, show_now=True, save_to=None):

        # Validate ts and bands selection.
        if n_bands != 1 and n_bands != 3:
            return None
        if stack is None:
            return None
        if color_table is not None and n_bands != 1:
            return None

        # Are we working with a color table?
        if n_bands == 1 and color_table is not None:
            d = np.array(stack, dtype=int)
            d = np.squeeze(d, axis=0)
            lookup = np.zeros(shape=(max([int(x) for x in color_table.keys()]) + 1, 4))
            for k in color_table.keys():
                lookup[int(k)] = color_table[k]
            d = lookup[d]
            mode = "RGBA"
            image = Image.fromarray(np.array(d, dtype=np.uint8), mode=mode)
        else:
            # Else, normalizes to 0 to 1.
            d = np.array(stack, dtype=np.float)
            v_min, v_max = np.nanmin(d), np.nanmax(d)
            r = 1.0 if v_max == v_min else v_max - v_min
            d -= v_min
            d *= 255.0 / float(r)
            mode = "RGB" if n_bands == 3 else "L"
            d = d if n_bands == 3 else np.squeeze(d, axis=-1)
            d = np.squeeze(d, axis=0)
            image = Image.fromarray(np.array(d, dtype=np.uint8), mode=mode)

        if mask is not None:
            mask = np.clip(mask * 255, None, 255)
            mask = Image.fromarray(np.array(mask, dtype=np.uint8), mode="L")
            image.putalpha(mask)

        if show_now:
            image.show()
        if save_to is not None:
            image.save(save_to)
