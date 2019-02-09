import time
import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa
from imgaug.augmenters import meta
from imgaug import parameters as iap
from imgaug import dtypes as iadt
import cv2
import skimage.data


def main():
    iterations = 100
    image = ia.imresize_single_image(skimage.data.astronaut(), (224, 224))
    images = np.uint8([image] * 128)
    m1 = AddElementwiseM1((-10, 10))
    m2 = AddElementwiseM2((-10, 10))
    m3 = AddElementwiseM3((-10, 10))

    for aug in [m1, m2, m3]:
        times = []
        for _ in range(iterations):
            start_time = time.time()
            _images_aug = aug.augment_images(images)
            times.append(time.time() - start_time)
        print(aug.__class__.__name__, np.min(times), np.average(times), np.max(times))


# default method
class AddElementwiseM1(meta.Augmenter):
    def __init__(self, value=0, per_channel=False, name=None, deterministic=False, random_state=None):
        super(AddElementwiseM1, self).__init__(name=name, deterministic=deterministic, random_state=random_state)

        # TODO open to continous, similar to Add
        self.value = iap.handle_discrete_param(value, "value", value_range=(-255, 255), tuple_to_uniform=True,
                                               list_to_choice=True, allow_floats=False)
        self.per_channel = iap.handle_probability_param(per_channel, "per_channel")

    def _augment_images(self, images, random_state, parents, hooks):
        ia.gate_dtypes(images,
                       allowed=["bool", "uint8", "uint16", "int8", "int16", "float16", "float32"],
                       disallowed=["uint32", "uint64", "uint128", "uint256", "int32", "int64", "int128", "int256",
                                   "float64", "float96", "float128", "float256"],
                       augmenter=self)

        input_dtypes = iadt.copy_dtypes_for_restore(images, force_list=True)

        nb_images = len(images)
        rss = ia.derive_random_states(random_state, nb_images+1)
        per_channel_samples = self.per_channel.draw_samples((nb_images,), random_state=rss[-1])

        gen = enumerate(zip(images, per_channel_samples, rss[:-1], input_dtypes))
        for i, (image, per_channel_samples_i, rs, input_dtype) in gen:
            height, width, nb_channels = image.shape
            sample_shape = (height, width, nb_channels if per_channel_samples_i > 0.5 else 1)
            value = self.value.draw_samples(sample_shape, random_state=rs)

            if image.dtype.name == "uint8":
                # This special uint8 block is around 60-100% faster than the else-block further below (more speedup
                # for smaller images).
                #
                # Also tested to instead compute min/max of image and value and then only convert image/value dtype
                # if actually necessary, but that was like 20-30% slower, even for 224x224 images.
                #
                if value.dtype.kind == "f":
                    value = np.round(value)

                image = image.astype(np.int16)
                value = np.clip(value, -255, 255).astype(np.int16)

                image_aug = image + value
                image_aug = np.clip(image_aug, 0, 255).astype(np.uint8)

                images[i] = image_aug
            else:
                # We limit here the value range of the value parameter to the bytes in the image's dtype.
                # This prevents overflow problems and makes it less likely that the image has to be up-casted, which
                # again improves performance and saves memory. Note that this also enables more dtypes for image inputs.
                # The downside is that the mul parameter is limited in its value range.
                #
                # We need 2* the itemsize of the image here to allow to shift the image's max value to the lowest
                # possible value, e.g. for uint8 it must allow for -255 to 255.
                itemsize = image.dtype.itemsize * 2
                dtype_target = np.dtype("%s%d" % (value.dtype.kind, itemsize))
                value = meta.clip_to_dtype_value_range_(value, dtype_target, validate=100)

                if value.shape[2] == 1:
                    value = np.tile(value, (1, 1, nb_channels))

                image, value = meta.promote_array_dtypes_([image, value], dtypes=[image.dtype, dtype_target],
                                                          increase_itemsize_factor=2)
                image = np.add(image, value, out=image, casting="no")
                image = iadt.restore_dtypes_(image, input_dtype)
                images[i] = image

        return images

    def _augment_heatmaps(self, heatmaps, random_state, parents, hooks):
        return heatmaps

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return [self.value, self.per_channel]


# convolve, repeat
class AddElementwiseM2(meta.Augmenter):
    def __init__(self, value=0, per_channel=False, name=None, deterministic=False, random_state=None):
        super(AddElementwiseM2, self).__init__(name=name, deterministic=deterministic, random_state=random_state)

        # TODO open to continous, similar to Add
        self.value = iap.handle_discrete_param(value, "value", value_range=(-255, 255), tuple_to_uniform=True,
                                               list_to_choice=True, allow_floats=False)
        self.per_channel = iap.handle_probability_param(per_channel, "per_channel")

    def _augment_images(self, images, random_state, parents, hooks):
        ia.gate_dtypes(images,
                       allowed=["bool", "uint8", "uint16", "int8", "int16", "float16", "float32"],
                       disallowed=["uint32", "uint64", "uint128", "uint256", "int32", "int64", "int128", "int256",
                                   "float64", "float96", "float128", "float256"],
                       augmenter=self)

        input_dtypes = iadt.copy_dtypes_for_restore(images, force_list=True)

        nb_images = len(images)
        rss = ia.derive_random_states(random_state, nb_images+1)
        per_channel_samples = self.per_channel.draw_samples((nb_images,), random_state=rss[-1])

        matrix = np.float32([1.0, 1.0]).T
        gen = enumerate(zip(images, per_channel_samples, rss[:-1], input_dtypes))
        for i, (image, per_channel_samples_i, rs, input_dtype) in gen:
            height, width, nb_channels = image.shape
            sample_shape = (height, width, nb_channels if per_channel_samples_i > 0.5 else 1)
            value = self.value.draw_samples(sample_shape, random_state=rs)

            if image.dtype.name == "uint8":
                image = np.repeat(image, 2, axis=0)
                if value.shape[2] != image.shape[2]:
                    image[::2, :, :] = np.tile(value, (1, 1, image.shape[2]))
                else:
                    image[::2, :, :] = value

                image_aug = cv2.filter2D(image, -1, matrix)

                images[i] = image_aug[::2, :, :]
            else:
                # We limit here the value range of the value parameter to the bytes in the image's dtype.
                # This prevents overflow problems and makes it less likely that the image has to be up-casted, which
                # again improves performance and saves memory. Note that this also enables more dtypes for image inputs.
                # The downside is that the mul parameter is limited in its value range.
                #
                # We need 2* the itemsize of the image here to allow to shift the image's max value to the lowest
                # possible value, e.g. for uint8 it must allow for -255 to 255.
                itemsize = image.dtype.itemsize * 2
                dtype_target = np.dtype("%s%d" % (value.dtype.kind, itemsize))
                value = iadt.clip_to_dtype_value_range_(value, dtype_target, validate=100)

                if value.shape[2] == 1:
                    value = np.tile(value, (1, 1, nb_channels))

                image, value = iadt.promote_array_dtypes_([image, value], dtypes=[image.dtype, dtype_target],
                                                          increase_itemsize_factor=2)
                image = np.add(image, value, out=image, casting="no")
                image = iadt.restore_dtypes_(image, input_dtype)
                images[i] = image

        return images

    def _augment_heatmaps(self, heatmaps, random_state, parents, hooks):
        return heatmaps

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return [self.value, self.per_channel]


# convolve, zeros+fill
class AddElementwiseM3(meta.Augmenter):
    def __init__(self, value=0, per_channel=False, name=None, deterministic=False, random_state=None):
        super(AddElementwiseM3, self).__init__(name=name, deterministic=deterministic, random_state=random_state)

        # TODO open to continous, similar to Add
        self.value = iap.handle_discrete_param(value, "value", value_range=(-255, 255), tuple_to_uniform=True,
                                               list_to_choice=True, allow_floats=False)
        self.per_channel = iap.handle_probability_param(per_channel, "per_channel")

    def _augment_images(self, images, random_state, parents, hooks):
        ia.gate_dtypes(images,
                       allowed=["bool", "uint8", "uint16", "int8", "int16", "float16", "float32"],
                       disallowed=["uint32", "uint64", "uint128", "uint256", "int32", "int64", "int128", "int256",
                                   "float64", "float96", "float128", "float256"],
                       augmenter=self)

        input_dtypes = iadt.copy_dtypes_for_restore(images, force_list=True)

        nb_images = len(images)
        rss = ia.derive_random_states(random_state, nb_images+1)
        per_channel_samples = self.per_channel.draw_samples((nb_images,), random_state=rss[-1])

        matrix = np.float32([1.0, 1.0]).T
        gen = enumerate(zip(images, per_channel_samples, rss[:-1], input_dtypes))
        for i, (image, per_channel_samples_i, rs, input_dtype) in gen:
            height, width, nb_channels = image.shape
            sample_shape = (height, width, nb_channels if per_channel_samples_i > 0.5 else 1)
            value = self.value.draw_samples(sample_shape, random_state=rs)

            if image.dtype.name == "uint8":
                image_container = np.zeros((image.shape[0]*2, image.shape[1], image.shape[2]), dtype=image.dtype)
                image_container[1::2, :, :] = image
                image = image_container
                #if value.shape[2] != image.shape[2]:
                #    image[::2, :, :] = np.tile(value, (1, 1, image.shape[2]))
                #else:
                #print("v", value[:10, 0, 0])
                #print("b", image[:10, 0, 0])
                #print("b", image[:10, 0, 1])
                image[::2, :, :] = value
                #print("a", image[:10, 0, 0])
                #print("a", image[:10, 0, 1])

                image_aug = cv2.filter2D(image, -1, matrix)

                images[i] = image_aug[::2, :, :]
            else:
                # We limit here the value range of the value parameter to the bytes in the image's dtype.
                # This prevents overflow problems and makes it less likely that the image has to be up-casted, which
                # again improves performance and saves memory. Note that this also enables more dtypes for image inputs.
                # The downside is that the mul parameter is limited in its value range.
                #
                # We need 2* the itemsize of the image here to allow to shift the image's max value to the lowest
                # possible value, e.g. for uint8 it must allow for -255 to 255.
                itemsize = image.dtype.itemsize * 2
                dtype_target = np.dtype("%s%d" % (value.dtype.kind, itemsize))
                value = iadt.clip_to_dtype_value_range_(value, dtype_target, validate=100)

                if value.shape[2] == 1:
                    value = np.tile(value, (1, 1, nb_channels))

                image, value = iadt.promote_array_dtypes_([image, value], dtypes=[image.dtype, dtype_target],
                                                          increase_itemsize_factor=2)
                image = np.add(image, value, out=image, casting="no")
                image = iadt.restore_dtypes_(image, input_dtype)
                images[i] = image

        return images

    def _augment_heatmaps(self, heatmaps, random_state, parents, hooks):
        return heatmaps

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return [self.value, self.per_channel]


# convolve, zeros+fill
class AddElementwiseM4(meta.Augmenter):
    def __init__(self, value=0, per_channel=False, name=None, deterministic=False, random_state=None):
        super(AddElementwiseM4, self).__init__(name=name, deterministic=deterministic, random_state=random_state)

        # TODO open to continous, similar to Add
        self.value = iap.handle_discrete_param(value, "value", value_range=(-255, 255), tuple_to_uniform=True,
                                               list_to_choice=True, allow_floats=False)
        self.per_channel = iap.handle_probability_param(per_channel, "per_channel")

    def _augment_images(self, images, random_state, parents, hooks):
        ia.gate_dtypes(images,
                       allowed=["bool", "uint8", "uint16", "int8", "int16", "float16", "float32"],
                       disallowed=["uint32", "uint64", "uint128", "uint256", "int32", "int64", "int128", "int256",
                                   "float64", "float96", "float128", "float256"],
                       augmenter=self)

        input_dtypes = iadt.copy_dtypes_for_restore(images, force_list=True)

        nb_images = len(images)
        rss = ia.derive_random_states(random_state, nb_images+1)
        per_channel_samples = self.per_channel.draw_samples((nb_images,), random_state=rss[-1])

        matrix = np.float32([1.0, 1.0]).T
        gen = enumerate(zip(images, per_channel_samples, rss[:-1], input_dtypes))
        for i, (image, per_channel_samples_i, rs, input_dtype) in gen:
            height, width, nb_channels = image.shape
            sample_shape = (height, width, nb_channels if per_channel_samples_i > 0.5 else 1)
            value = self.value.draw_samples(sample_shape, random_state=rs)

            if image.dtype.name == "uint8":
                image_container = np.zeros((image.shape[0]*2, image.shape[1], image.shape[2]), dtype=image.dtype)
                image_container[1::2, :, :] = image
                image = image_container
                #if value.shape[2] != image.shape[2]:
                #    image[::2, :, :] = np.tile(value, (1, 1, image.shape[2]))
                #else:
                #print("v", value[:10, 0, 0])
                #print("b", image[:10, 0, 0])
                #print("b", image[:10, 0, 1])
                image[::2, :, :] = value
                #print("a", image[:10, 0, 0])
                #print("a", image[:10, 0, 1])

                image_aug = cv2.filter2D(image, -1, matrix)

                images[i] = image_aug[::2, :, :]
            else:
                # We limit here the value range of the value parameter to the bytes in the image's dtype.
                # This prevents overflow problems and makes it less likely that the image has to be up-casted, which
                # again improves performance and saves memory. Note that this also enables more dtypes for image inputs.
                # The downside is that the mul parameter is limited in its value range.
                #
                # We need 2* the itemsize of the image here to allow to shift the image's max value to the lowest
                # possible value, e.g. for uint8 it must allow for -255 to 255.
                itemsize = image.dtype.itemsize * 2
                dtype_target = np.dtype("%s%d" % (value.dtype.kind, itemsize))
                value = iadt.clip_to_dtype_value_range_(value, dtype_target, validate=100)

                if value.shape[2] == 1:
                    value = np.tile(value, (1, 1, nb_channels))

                image, value = iadt.promote_array_dtypes_([image, value], dtypes=[image.dtype, dtype_target],
                                                          increase_itemsize_factor=2)
                image = np.add(image, value, out=image, casting="no")
                image = iadt.restore_dtypes_(image, input_dtype)
                images[i] = image

        return images

    def _augment_heatmaps(self, heatmaps, random_state, parents, hooks):
        return heatmaps

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return [self.value, self.per_channel]


if __name__ == "__main__":
    main()
