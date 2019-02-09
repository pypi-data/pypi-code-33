from __future__ import print_function, division
import cv2
import numpy as np
from collections import OrderedDict
from skimage import transform
import time

np.random.seed(42)

NEW_RESOLUTIONS = [
    (32, 32),
    (128, 128)
]

HEIGHT = 64
WIDTH = 64

def main():
    # -----------------
    # Supported dtypes
    # -----------------
    """
    cv2 <type 'numpy.float16'>: [False, False]
    cv2 <type 'numpy.float32'>: [True, True]
    cv2 <type 'numpy.float64'>: [True, True]
    cv2 <type 'numpy.float128'>: [False, False]
    cv2 <type 'numpy.int8'>: [False, False]
    cv2 <type 'numpy.int16'>: [True, True]
    cv2 <type 'numpy.int32'>: [False, False]
    cv2 <type 'numpy.int64'>: [False, False]
    cv2 <type 'numpy.uint8'>: [True, True]
    cv2 <type 'numpy.uint16'>: [True, True]
    cv2 <type 'numpy.uint32'>: [False, False]
    cv2 <type 'numpy.uint64'>: [False, False]
    skimage <type 'numpy.float16'>: [True, True]
    skimage <type 'numpy.float32'>: [True, True]
    skimage <type 'numpy.float64'>: [True, True]
    skimage <type 'numpy.float128'>: [False, False]
    skimage <type 'numpy.int8'>: [True, True]
    skimage <type 'numpy.int16'>: [True, True]
    skimage <type 'numpy.int32'>: [True, True]
    skimage <type 'numpy.int64'>: [False, False]
    skimage <type 'numpy.uint8'>: [True, True]
    skimage <type 'numpy.uint16'>: [True, True]
    skimage <type 'numpy.uint32'>: [True, True]
    skimage <type 'numpy.uint64'>: [False, False]

    cv2 <type 'numpy.float16'>: [False, False]
    cv2 <type 'numpy.float32'>: [True, True]
    cv2 <type 'numpy.float64'>: [True, True]
    cv2 <type 'numpy.float128'>: [False, False]
    cv2 <type 'numpy.int8'>: [False, False]
    cv2 <type 'numpy.int16'>: [True, True]
    cv2 <type 'numpy.int32'>: [False, False]
    cv2 <type 'numpy.int64'>: [False, False]
    cv2 <type 'numpy.uint8'>: [True, True]
    cv2 <type 'numpy.uint16'>: [True, True]
    cv2 <type 'numpy.uint32'>: [False, False]
    cv2 <type 'numpy.uint64'>: [False, False]
    skimage <type 'numpy.float16'>: [False, False]
    skimage <type 'numpy.float32'>: [False, False]
    skimage <type 'numpy.float64'>: [True, True]
    skimage <type 'numpy.float128'>: [False, False]
    skimage <type 'numpy.int8'>: [False, False]
    skimage <type 'numpy.int16'>: [False, False]
    skimage <type 'numpy.int32'>: [False, False]
    skimage <type 'numpy.int64'>: [False, False]
    skimage <type 'numpy.uint8'>: [False, False]
    skimage <type 'numpy.uint16'>: [False, False]
    skimage <type 'numpy.uint32'>: [False, False]
    skimage <type 'numpy.uint64'>: [False, False]

                cv2 | skimage
    uint8       X       X
    uint16      X       X
    uint32      -       X
    uint64      -       -
    int8        -       X
    int16       X       X
    int32       -       X
    int64       -       -
    float16     -       X
    float32     X       X
    float64     X       X
    float128    -       -

    """
    float_dtypes = np.sctypes["float"]
    int_dtypes = np.sctypes["int"]
    uint_dtypes = np.sctypes["uint"]
    results = OrderedDict()

    print("------------------")
    print("DTYPE ERROR AND PRESERVATION CHECK")
    print("------------------")
    for input_dtype in float_dtypes + int_dtypes + uint_dtypes:
        results[("cv2", input_dtype)] = []
        results[("skimage", input_dtype)] = []
        for height_new, width_new in NEW_RESOLUTIONS:
            image = dtype_to_image(input_dtype, HEIGHT, WIDTH)
            try:
                print("cv2 %s %dx%d" % (input_dtype, height_new, width_new))
                image_rs_cv2 = cv2.resize(image, (width_new, height_new), interpolation=cv2.INTER_LINEAR)
                assert image_rs_cv2.dtype == input_dtype
                if input_dtype in np.sctypes["int"] or input_dtype in np.sctypes["uint"]:
                    assert np.max(image_rs_cv2) > 1 + 1e-4
                #results[("cv2", height_new, width_new, input_dtype)] = True
                results[("cv2", input_dtype)].append(True)
            except Exception as e:
                print("----------------")
                print("cv2 error for dtype %s at %dx%d" % (input_dtype, height_new, width_new))
                print(e)
                print("----------------")
                #results[("cv2", height_new, width_new, input_dtype)] = False
                results[("cv2", input_dtype)].append(False)

            try:
                print("skimage %s %dx%d" % (input_dtype, height_new, width_new))
                image_rs_ski = transform.resize(image, (height_new, width_new), order=1, preserve_range=True)
                image_rs_ski = image_rs_ski.astype(input_dtype)
                assert image_rs_ski.dtype == input_dtype
                if input_dtype in np.sctypes["int"] or input_dtype in np.sctypes["uint"]:
                    assert np.max(image_rs_ski) > 1 + 1e-4
                #results[("skimage", height_new, width_new, input_dtype)] = True
                results[("skimage", input_dtype)].append(True)
            except Exception as e:
                print("----------------")
                print("skimage error for dtype %s at %dx%d" % (input_dtype, height_new, width_new))
                print(e)
                print("----------------")
                results[("skimage", input_dtype)].append(False)

    results_sorted = sorted(results.items(), key=lambda pair: pair[0][0])

    for key, val in results_sorted:
        #print("%s %dx%d %s %s" % (key[0], key[1], key[2], key[3], val))
        print("%s %s: %s" % (key[0], key[1], str(val)))


    # ------------
    # Timings
    # ------------
    print("------------------")
    print("TIMINGS")
    print("------------------")
    cv2_dtypes = [np.uint8, np.uint16, np.int16, np.float32, np.float64]
    skimage_dtypes = [np.uint8, np.uint16, np.uint32, np.int8, np.int16, np.float32, np.float16, np.float32, np.float64]
    for input_dtype in cv2_dtypes:
        image = dtype_to_image(input_dtype, HEIGHT, WIDTH)
        time_start = time.time()
        for _ in xrange(1000):
            image_rs = cv2.resize(image, (NEW_RESOLUTIONS[0][1], NEW_RESOLUTIONS[0][0]), interpolation=cv2.INTER_LINEAR)
        time_end = time.time()
        print("cv2 %s: %.4f" % (input_dtype, time_end - time_start))
    for input_dtype in skimage_dtypes:
        image = dtype_to_image(input_dtype, HEIGHT, WIDTH)
        time_start = time.time()
        for _ in xrange(1000):
            image_rs = transform.resize(image, (NEW_RESOLUTIONS[0][0], NEW_RESOLUTIONS[0][1]), order=0, preserve_range=True)
        time_end = time.time()
        print("skimage %s: %.4f" % (input_dtype, time_end - time_start))

    # ------------
    # Similarity
    # ------------
    print("------------------")
    print("MEASURING SIMILARITIES")
    print("------------------")
    check_dtypes = [np.uint8, np.uint16, np.int16, np.float32, np.float64]
    cv2_modes = [cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_AREA, cv2.INTER_CUBIC]
    ski_orders = [0, 1, 2, 3, 4, 5]
    images = dict()
    for dtype in check_dtypes:
        image = dtype_to_image(input_dtype, HEIGHT, WIDTH)
        for cv2_mode in cv2_modes:
            image_rs = cv2.resize(image, (NEW_RESOLUTIONS[0][1], NEW_RESOLUTIONS[0][0]), interpolation=cv2_mode)
            images[(str(dtype), "cv2", cv2_mode)] = image_rs
        for ski_order in ski_orders:
            image_rs = transform.resize(image, (NEW_RESOLUTIONS[0][0], NEW_RESOLUTIONS[0][1]), order=ski_order, preserve_range=True)
            images[(str(dtype), "ski", ski_order)] = image_rs

    for key in images:
        if key[1] == "cv2":
            for key2 in images:
                if key2[0] == key[0] and key2[1] != "cv2":
                    closeness = np.average(np.abs(images[key] - images[key2]))
                    print("[%s] [%s <-> %s] [%s <-> %s] %s" % (key[0], key[1], key2[1], key[2], key2[2], closeness))

def dtype_to_image(dtype, height, width):
    if dtype in np.sctypes["float"]:
        return np.random.uniform(0.0, 1.0, size=(height, width, 1)).astype(dtype)
    elif dtype in np.sctypes["int"]:
        return np.random.randint(np.iinfo(dtype).min, np.iinfo(dtype).max, size=(height, width, 5), dtype=dtype)
    elif dtype in np.sctypes["uint"]:
        return np.random.randint(np.iinfo(dtype).min, np.iinfo(dtype).max, size=(height, width, 3), dtype=dtype)
    else:
        assert False

if __name__ == "__main__":
    main()
