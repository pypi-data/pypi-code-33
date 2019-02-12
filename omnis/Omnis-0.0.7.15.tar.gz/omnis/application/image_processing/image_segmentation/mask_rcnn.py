import os
import json
import numpy as np
import skimage.draw
import random
import cv2
from ...application import Application

# Import Mask RCNN
from mrcnn import model as modellib, utils, visualize


class Mask_RCNN(Application):
    def __init__(self):
        Application.__init__(self)
        self.config = Config()
        self.predict_image_from_val_dataset = True

    def mask(self, image_data, r, show_masked_image = True):
        if self.predict_image_from_val_dataset:
            visualize.display_instances(image_data[0], image_data[3], image_data[4], image_data[2],
                                        self.class_names, figsize=(8, 8), show_masked_image = show_masked_image)

        result = visualize.display_instances(image_data[0], r['rois'], r['masks'], r['class_ids'],
                                    self.class_names, r['scores'], show_masked_image = show_masked_image)

        return self.mask_to_json(result, r["id"])

    def mask_to_json(self, mask, filename):
        mask_list = []
        mask_dict = {"filename": filename}
        for i, m in enumerate(mask):
            x = []
            y = []
            for c in m:
                x.append(c[0])
                y.append(c[1])
            x_y_list = [["all_points_x", x], ["all_points_y", y]]
            x_y_list = dict(x_y_list)
            mask_list.append(["{}".format(i), x_y_list])
        mask_dict["regions"] = dict(mask_list)
        return json.dumps(mask_dict)

    def predict(self, weights_path, predict_image_path = None, predict_image_array = None, use_coco_config = False):
        if predict_image_path:
            try:
                predict_image = cv2.imread(predict_image_path)
                _, filename = os.path.split(predict_image_path)
                self.predict_image_from_val_dataset = False
            except Exception as e:
                raise e
        elif predict_image_array:
            if predict_image_array.ndim == 3:
                predict_image = predict_image_array
                filename = "predicted_mask_rcnn_image.png"
            else:
                raise ValueError("predict_image_array.ndim has to be 3")
            self.predict_image_from_val_dataset = False

        if use_coco_config:
        # Download weights file
            if not os.path.exists(weights_path):
                utils.download_trained_weights(weights_path)
            self.config.NUM_CLASSES = 1 + 80 # COCO has 80 classes
            self.class_names = ["BG", "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
                                "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                                "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
                                "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
                                "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
                                "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
                                "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
                                "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
                                "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
                                "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
            print("{} Classes: {}".format(len(self.class_names), self.class_names))

        self.config.__init__()
        self.config.display()

        model = modellib.MaskRCNN(mode="inference", config=self.config, model_dir='.')

        print("Loading weights from ", weights_path)
        model.load_weights(weights_path, by_name=True)

        if not self.predict_image_from_val_dataset:
            results = model.detect([predict_image], verbose=1)
            r = results[0]
            r["id"] = filename
            image_data = [predict_image]
        else:
            image_id = random.choice(self.dataset_val.image_ids)
            image_data = modellib.load_image_gt(self.dataset_val, self.config, image_id, use_mini_mask=False)
            
            modellib.log("original_image", image_data[0])
            modellib.log("image_meta", image_data[1])
            modellib.log("gt_class_id", image_data[2])
            modellib.log("gt_bbox", image_data[3])
            modellib.log("gt_mask", image_data[4])

            results = model.detect([image_data[0]], verbose=1)
            r = results[0]
            r["id"] = self.dataset_val.image_info[image_id]['id']

            # Compute mAP
            mAP, precisions, recalls, overlaps =\
                utils.compute_ap(image_data[3], image_data[2], image_data[4],
                                r["rois"], r["class_ids"], r["scores"], r['masks'])

            print("mAP: ", mAP)

        return image_data, r

    def prepare_train_data(self, data_path = None, get_image_from = 'directory', data_array = None):
        self.data_path = data_path
        self.get_image_from = get_image_from
        self.data_array = data_array

        if get_image_from == 'directory':
            assert data_path, "Provide data_path to train from directory"
        elif get_image_from == 'argument':
            assert data_array, "Provide data_array to train from argument"
        else:
            raise ValueError("value of get_image_from should be either 'directory' or 'argument'.")

        # Training dataset
        self.dataset_train = ImageDataset()
        self.dataset_train.load_class(self.data_path, "train")
        self.dataset_train.prepare()
        print("Images: {}\nClasses: {}".format(len(self.dataset_train.image_ids), self.dataset_train.class_names))
        self.config.NUM_CLASSES = len(self.dataset_train.class_names) # Background + other classes

        # Validation dataset
        self.dataset_val = ImageDataset()
        self.dataset_val.load_class(self.data_path, "val")
        self.dataset_val.prepare()
        print("Images: {}\nClasses: {}".format(len(self.dataset_val.image_ids), self.dataset_val.class_names))

        assert sorted(self.dataset_train.class_names) == sorted(self.dataset_val.class_names), "train classes have to be same with val classes"

        self.class_names = self.dataset_val.class_names

    def save(self, model, weights_path):
        model.keras_model.save_weights(weights_path)

    def train(self, epochs = 4, weights_path = None, images_per_gpu = 1, gpu_count = 1):
        """Train the model."""
        # 8GB VRAM can fit one image.
        # Adjust up if you use a larger GPU. (2 for 12GB)
        self.config.IMAGES_PER_GPU = images_per_gpu
        self.config.GPU_COUNT = gpu_count
        self.config.__init__()
        self.config.display()
        # Create model
        model = modellib.MaskRCNN(mode="training", config=self.config, model_dir='.')
        
        # Download weights file
        if not os.path.exists(weights_path):
            utils.download_trained_weights(weights_path)

        # Load weights
        print("Loading weights ", weights_path)

        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])

        # Train
        print("Training network heads")
        model.train(self.dataset_train, self.dataset_val,
                    learning_rate=0.001,
                    epochs=epochs,
                    layers='heads')

        return model

class ImageDataset(utils.Dataset):
    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "source":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)

    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a shape dataset image, delegate to parent class.
        image_info = self.image_info[image_id]
        if image_info["source"] != "source":
            return super(self.__class__, self).load_mask(image_id)

        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
            mask[rr, cc, i] = 1
        # Return mask, and array of class IDs of each instance.
        if info["class_ids"]:
            class_ids = np.array(info["class_ids"], dtype = np.int32)
            return mask.astype(np.bool), class_ids
        else:
            return super(self.__class__, self).load_mask(image_id)

    def load_class(self, dataset_dir, subset):
        """Load a subset of the dataset.
        dataset_dir: Root directory of the dataset.
        subset: Subset to load: train or val
        """
        # Train or validation dataset?
        assert subset in ["train", "val"]

        dataset_dir = os.path.join(dataset_dir, subset)

        # Load annotations
        # VGG Image Annotator (up to version 1.6) saves each image in the form:
        # { 'filename': '28503151_5b5b7ec140_b.jpg',
        #   'regions': {
        #       '0': {
        #           'region_attributes': {},
        #           'shape_attributes': {
        #               'all_points_x': [...],
        #               'all_points_y': [...],
        #               'name': 'polygon'}},
        #       ... more regions ...
        #   },
        #   'size': 100202
        # }
        # We mostly care about the x and y coordinates of each region
        # Note: In VIA 2.0, regions was changed from a dict to a list.
        annotations = json.load(open(os.path.join(dataset_dir, "via_region_data.json")))
        annotations = list(annotations.values())  # don't need the dict keys

        # The VIA tool saves images in the JSON even if they don't have any
        # annotations. Skip unannotated images.
        annotations = [a for a in annotations if a['regions']]

        # Add images
        for a in annotations:
            # Get the x, y coordinates of points of the polygons that make up
            # the outline of each object instance. These are stores in the
            # shape_attributes (see json format above)
            # The if condition is needed to support VIA versions 1.x and 2.x.
            i = 0
            class_ids = []
            class_list = []
            if type(a['regions']) is dict:
                polygons = []
                for r in a['regions'].values():
                    polygons.append(r['shape_attributes'])
                    c = r['region_attributes']['class']
                    if c not in class_list:
                        i += 1
                        class_list.append(c)
                        self.add_class("source",i,c)
                        class_ids.append(i)
                    else:
                        class_ids.append(class_list.index(c) + 1)

            else:
                polygons = []
                for r in a['regions']:
                    polygons.append(r['shape_attributes'])
                    c = r['region_attributes']['class']
                    if c not in class_list:
                        i += 1
                        class_list.append(c)
                        self.add_class("source",i,c)
                        class_ids.append(i)
                    else:
                        class_ids.append(class_list.index(c) + 1)

            # load_mask() needs the image size to convert polygons to masks.
            # Unfortunately, VIA doesn't include it in JSON, so we must read
            # the image. This is only managable since the dataset is tiny.
            image_path = os.path.join(dataset_dir, a['filename'])
            image = cv2.imread(image_path)
            height, width = image.shape[:2]

            self.add_image(
                "source",
                image_id=a['filename'],  # use file name as a unique image id
                path=image_path,
                width=width, height=height,
                polygons=polygons,
                class_ids = class_ids)

class Config(object):
    """Base configuration class. For custom configurations, create a
    sub-class that inherits from this one and override properties
    that need to be changed.
    """
    # Name the configurations. For example, 'COCO', 'Experiment 3', ...etc.
    # Useful if your code needs to do things differently depending on which
    # experiment is running.
    NAME = "source"

    # NUMBER OF GPUs to use. When using only a CPU, this needs to be set to 1.
    GPU_COUNT = 1

    # Number of images to train with on each GPU. A 12GB GPU can typically
    # handle 2 images of 1024x1024px.
    # Adjust based on your GPU memory and image sizes. Use the highest
    # number that your GPU can handle for best performance.
    IMAGES_PER_GPU = 1

    # Number of training steps per epoch
    # This doesn't need to match the size of the training set. Tensorboard
    # updates are saved at the end of each epoch, so setting this to a
    # smaller number means getting more frequent TensorBoard updates.
    # Validation stats are also calculated at each epoch end and they
    # might take a while, so don't set this too small to avoid spending
    # a lot of time on validation stats.
    STEPS_PER_EPOCH = 100

    # Number of validation steps to run at the end of every training epoch.
    # A bigger number improves accuracy of validation stats, but slows
    # down the training.
    VALIDATION_STEPS = 50

    # Backbone network architecture
    # Supported values are: resnet50, resnet101.
    # You can also provide a callable that should have the signature
    # of model.resnet_graph. If you do so, you need to supply a callable
    # to COMPUTE_BACKBONE_SHAPE as well
    BACKBONE = "resnet101"

    # Only useful if you supply a callable to BACKBONE. Should compute
    # the shape of each layer of the FPN Pyramid.
    # See model.compute_backbone_shapes
    COMPUTE_BACKBONE_SHAPE = None

    # The strides of each layer of the FPN Pyramid. These values
    # are based on a Resnet101 backbone.
    BACKBONE_STRIDES = [4, 8, 16, 32, 64]

    # Size of the fully-connected layers in the classification graph
    FPN_CLASSIF_FC_LAYERS_SIZE = 1024

    # Size of the top-down layers used to build the feature pyramid
    TOP_DOWN_PYRAMID_SIZE = 256

    # Number of classification classes (including background)
    NUM_CLASSES = 1  # Override in sub-classes

    # Length of square anchor side in pixels
    RPN_ANCHOR_SCALES = (32, 64, 128, 256, 512)

    # Ratios of anchors at each cell (width/height)
    # A value of 1 represents a square anchor, and 0.5 is a wide anchor
    RPN_ANCHOR_RATIOS = [0.5, 1, 2]

    # Anchor stride
    # If 1 then anchors are created for each cell in the backbone feature map.
    # If 2, then anchors are created for every other cell, and so on.
    RPN_ANCHOR_STRIDE = 1

    # Non-max suppression threshold to filter RPN proposals.
    # You can increase this during training to generate more propsals.
    RPN_NMS_THRESHOLD = 0.7

    # How many anchors per image to use for RPN training
    RPN_TRAIN_ANCHORS_PER_IMAGE = 256
    
    # ROIs kept after tf.nn.top_k and before non-maximum suppression
    PRE_NMS_LIMIT = 6000

    # ROIs kept after non-maximum suppression (training and inference)
    POST_NMS_ROIS_TRAINING = 2000
    POST_NMS_ROIS_INFERENCE = 1000

    # If enabled, resizes instance masks to a smaller size to reduce
    # memory load. Recommended when using high-resolution images.
    USE_MINI_MASK = True
    MINI_MASK_SHAPE = (56, 56)  # (height, width) of the mini-mask

    # Input image resizing
    # Generally, use the "square" resizing mode for training and predicting
    # and it should work well in most cases. In this mode, images are scaled
    # up such that the small side is = IMAGE_MIN_DIM, but ensuring that the
    # scaling doesn't make the long side > IMAGE_MAX_DIM. Then the image is
    # padded with zeros to make it a square so multiple images can be put
    # in one batch.
    # Available resizing modes:
    # none:   No resizing or padding. Return the image unchanged.
    # square: Resize and pad with zeros to get a square image
    #         of size [max_dim, max_dim].
    # pad64:  Pads width and height with zeros to make them multiples of 64.
    #         If IMAGE_MIN_DIM or IMAGE_MIN_SCALE are not None, then it scales
    #         up before padding. IMAGE_MAX_DIM is ignored in this mode.
    #         The multiple of 64 is needed to ensure smooth scaling of feature
    #         maps up and down the 6 levels of the FPN pyramid (2**6=64).
    # crop:   Picks random crops from the image. First, scales the image based
    #         on IMAGE_MIN_DIM and IMAGE_MIN_SCALE, then picks a random crop of
    #         size IMAGE_MIN_DIM x IMAGE_MIN_DIM. Can be used in training only.
    #         IMAGE_MAX_DIM is not used in this mode.
    IMAGE_RESIZE_MODE = "square"
    IMAGE_MIN_DIM = 800
    IMAGE_MAX_DIM = 1024
    # Minimum scaling ratio. Checked after MIN_IMAGE_DIM and can force further
    # up scaling. For example, if set to 2 then images are scaled up to double
    # the width and height, or more, even if MIN_IMAGE_DIM doesn't require it.
    # Howver, in 'square' mode, it can be overruled by IMAGE_MAX_DIM.
    IMAGE_MIN_SCALE = 0
    # Number of color channels per image. RGB = 3, grayscale = 1, RGB-D = 4
    # Changing this requires other changes in the code. See the WIKI for more
    # details: https://github.com/matterport/Mask_RCNN/wiki
    IMAGE_CHANNEL_COUNT = 3

    # Image mean (RGB)
    MEAN_PIXEL = np.array([123.7, 116.8, 103.9])

    # Number of ROIs per image to feed to classifier/mask heads
    # The Mask RCNN paper uses 512 but often the RPN doesn't generate
    # enough positive proposals to fill this and keep a positive:negative
    # ratio of 1:3. You can increase the number of proposals by adjusting
    # the RPN NMS threshold.
    TRAIN_ROIS_PER_IMAGE = 200

    # Percent of positive ROIs used to train classifier/mask heads
    ROI_POSITIVE_RATIO = 0.33

    # Pooled ROIs
    POOL_SIZE = 7
    MASK_POOL_SIZE = 14

    # Shape of output mask
    # To change this you also need to change the neural network mask branch
    MASK_SHAPE = [28, 28]

    # Maximum number of ground truth instances to use in one image
    MAX_GT_INSTANCES = 100

    # Bounding box refinement standard deviation for RPN and final detections.
    RPN_BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])
    BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])

    # Max number of final detections
    DETECTION_MAX_INSTANCES = 100

    # Minimum probability value to accept a detected instance
    # ROIs below this threshold are skipped
    DETECTION_MIN_CONFIDENCE = 0.7

    # Non-maximum suppression threshold for detection
    DETECTION_NMS_THRESHOLD = 0.3

    # Learning rate and momentum
    # The Mask RCNN paper uses lr=0.02, but on TensorFlow it causes
    # weights to explode. Likely due to differences in optimizer
    # implementation.
    LEARNING_RATE = 0.001
    LEARNING_MOMENTUM = 0.9

    # Weight decay regularization
    WEIGHT_DECAY = 0.0001

    # Loss weights for more precise optimization.
    # Can be used for R-CNN training setup.
    LOSS_WEIGHTS = {
        "rpn_class_loss": 1.,
        "rpn_bbox_loss": 1.,
        "mrcnn_class_loss": 1.,
        "mrcnn_bbox_loss": 1.,
        "mrcnn_mask_loss": 1.
    }

    # Use RPN ROIs or externally generated ROIs for training
    # Keep this True for most situations. Set to False if you want to train
    # the head branches on ROI generated by code rather than the ROIs from
    # the RPN. For example, to debug the classifier head without having to
    # train the RPN.
    USE_RPN_ROIS = True

    # Train or freeze batch normalization layers
    #     None: Train BN layers. This is the normal mode
    #     False: Freeze BN layers. Good when using a small batch size
    #     True: (don't use). Set layer in training mode even when predicting
    TRAIN_BN = False  # Defaulting to False since batch size is often small

    # Gradient norm clipping
    GRADIENT_CLIP_NORM = 5.0

    def __init__(self):
        """Set values of computed attributes."""
        # Effective batch size
        self.BATCH_SIZE = self.IMAGES_PER_GPU * self.GPU_COUNT

        # Input image size
        if self.IMAGE_RESIZE_MODE == "crop":
            self.IMAGE_SHAPE = np.array([self.IMAGE_MIN_DIM, self.IMAGE_MIN_DIM,
                self.IMAGE_CHANNEL_COUNT])
        else:
            self.IMAGE_SHAPE = np.array([self.IMAGE_MAX_DIM, self.IMAGE_MAX_DIM,
                self.IMAGE_CHANNEL_COUNT])

        # Image meta data length
        # See compose_image_meta() for details
        self.IMAGE_META_SIZE = 1 + 3 + 3 + 4 + 1 + self.NUM_CLASSES

    def display(self):
        """Display Configuration values."""
        print("\nConfigurations:")
        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                print("{:30} {}".format(a, getattr(self, a)))
        print("\n")
