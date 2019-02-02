"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod
import os
from typing import List, Tuple

import numpy
from tensorflow.python.client.session import InteractiveSession as tf_InteractiveSession
from tensorflow import image as tf_image

from pyjamas.rimage.rimutils import rimutils
from pyjamas.rimage import rimclassifier
from .featurecalculator import FeatureCalculator
from .featurecalculator_sog import FeatureCalculatorSOG


class rimclassifier(ABC):
    DEFAULT_STEP_SZ: Tuple[int, int] = (5, 5)  # For SVM at least, when this parameter equals 1 more objects are
    # recognized than when it equals 5.

    # These define default values for non-maximum supression.
    DEFAULT_IOU_THRESHOLD: float = .33  # When iou_threshold (intersection/union) is small, fewer boxes are left,
    # as boxes with overlap above the threshold are suppressed.
    DEFAULT_PROB_THRESHOLD: float = .95
    DEFAULT_MAX_NUM_OBJECTS: int = 200

    CLASSIFIER_EXTENSION: str = '.cfr'

    def __init__(self, parameters: dict = None):
        self.positive_training_folder: str = parameters['positive_training_folder']
        self.negative_training_folder: str = parameters['negative_training_folder']
        self.hard_negative_training_folder: str = parameters['hard_negative_training_folder']

        # Size of training images (rows, columns).
        self.train_image_size: Tuple[int, int] = parameters['train_image_size']

        # Feature calculator.
        self.fc: FeatureCalculator = parameters.get('fc', FeatureCalculatorSOG())

        # Classifier: SVC, DecisionTreeClassifier, etc.
        self.classifier = None

        # Scanning parameters.
        self.step_sz: Tuple[int, int] = parameters.get('step_sz', rimclassifier.DEFAULT_STEP_SZ)  # For SVM at least, when this parameter equals 1 more objects are recognized than when it equals 5.

        # Non-max suppression.
        self.iou_threshold: float = parameters.get('iou_threshold', rimclassifier.DEFAULT_IOU_THRESHOLD)  # When iou_threshold (intersection/union) is small, fewer boxes are left, as boxes with overlap above the threshold are suppressed.
        self.prob_threshold: float = parameters.get('prob_threshold', rimclassifier.DEFAULT_PROB_THRESHOLD) # Boxes below this probability will be ignored.
        self.max_num_objects: int = parameters.get('max_num_objects_dial', rimclassifier.DEFAULT_MAX_NUM_OBJECTS)

        self.tf_session: tf_InteractiveSession = None
        self.good_box_indices: numpy.ndarray = None

        # Classifier features.
        self.features_positive_array: numpy.ndarray = None
        self.features_negative_array: numpy.ndarray = None

        # Test parameters.
        self.object_positions: list = None
        self.object_map: numpy.ndarray = None
        self.box_array: numpy.ndarray = None
        self.prob_array: numpy.ndarray = None

    def compute_features(self, folder: str = None) -> numpy.ndarray:
        if self.fc is None or self.fc is False or not os.path.exists(folder):
            return numpy.empty((1,))

        features: numpy.ndarray = None

        # List files in the folder.
        thefiles: List[str] = os.listdir(folder)

        # For each file:
        for f in thefiles:

            # If it is not a directory, read the image, calculate the hog features and append to a list.
            # (this is apparently faster than appending to an ndarray:
            # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

            thepath = os.path.join(folder, f)

            if os.path.isfile(thepath):
                # Read the file as an image. @todo: this may throw an exception.
                image = rimutils.read_stack(thepath)
                image = numpy.squeeze(image)

                # Calculate hog features and append to the list.
                self.fc.calculate_features(image)
                if features is None:
                    features = self.fc.gimme_features()
                else:
                    features = numpy.vstack((features, self.fc.gimme_features()))

        return features

    @abstractmethod
    def fit(self) -> bool:
        pass

    @abstractmethod
    def hard_negative_mining(self) -> bool:
        pass

    @abstractmethod
    def predict(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        pass

    @abstractmethod
    def save_classifier(self, filename: str) -> bool:
        pass

    def non_max_suppression(self, box_array: numpy.ndarray, prob_array: numpy.ndarray, prob_threshold_fn: float, iou_threshold_fn: float, max_num_objects_fn: int) -> numpy.ndarray:
        if box_array is None or box_array is False:
            return None

        if prob_array is None or prob_array is False:
            return None

        if max_num_objects_fn is None or max_num_objects_fn is False:
            max_num_objects_fn = self.max_num_objects
        else:
            self.max_num_objects = max_num_objects_fn

        if prob_threshold_fn is None or prob_threshold_fn is False:
            prob_threshold_fn = self.prob_threshold
        else:
            self.prob_threshold = prob_threshold_fn

        if iou_threshold_fn is None or iou_threshold_fn is False:
            iou_threshold_fn = self.iou_threshold
        else:
            self.iou_threshold = iou_threshold_fn

        # Trying to use tensorflow here: https://www.tensorflow.org/api_docs/python/tf/image/non_max_suppression
        # Other methods: http://openaccess.thecvf.com/content_cvpr_2017/papers/Hosang_Learning_Non-Maximum_Suppression_CVPR_2017_paper.pdf

        # Initialize tensorflow (used for non-max suppression).
        if not self.tf_session:
            self.tf_session = tf_InteractiveSession()

        good_box_indices_tensor = tf_image.non_max_suppression(box_array, prob_array,
                                                               max_output_size=max_num_objects_fn,
                                                               iou_threshold=iou_threshold_fn,
                                                               score_threshold=prob_threshold_fn)
        self.good_box_indices = good_box_indices_tensor.eval(session=self.tf_session)
        #good_box_array = self.box_array[good_box_indices]

        return self.good_box_indices.copy()

    def find_objects(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        """
        Combine predict and non_max_suppression.

        :param image:
        :return:
        """
        box_array, prob_array = self.predict(image)
        good_box_indices = self.non_max_suppression(self.prob_threshold, self.iou_threshold, self.max_num_objects)

        return box_array[good_box_indices], prob_array[good_box_indices]

