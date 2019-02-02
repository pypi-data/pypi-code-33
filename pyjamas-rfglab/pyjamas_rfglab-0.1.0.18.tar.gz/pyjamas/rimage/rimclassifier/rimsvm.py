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

import gzip
import os
import pickle

import numpy
from sklearn.svm import SVC

from .rimclassifier import rimclassifier
from ..rimutils import rimutils


class svm(rimclassifier):
    KERNEL_TYPES = ('linear', )

    DEFAULT_KERNEL_TYPE: int = 0
    DEFAULT_C: float = 1.0  # Missed class penalty: small values (0.05) result in some additional nuclei detected and others

    # not. Large values (100) do not seem to change the result with respect to 1.0.
    # Should featurecalculator be a class attribute?

    def __init__(self, parameters: dict = None):
        super().__init__(parameters)

        # SVM-specific parameters.
        self.misclass_penalty_C: float = parameters.get('C', svm.DEFAULT_C)
        self.kernel_type: int = parameters.get('kernel_type', svm.DEFAULT_KERNEL_TYPE)
        self.classifier = parameters.get('classifier', SVC(kernel=svm.KERNEL_TYPES[self.kernel_type], C=self.misclass_penalty_C,
                                       random_state=1, probability=True))

    ### THIS IS WAY TOO FAST COMPARED TO SCRIPT. WHAT IS HAPPENING!!??
    # HARD NEGATIVE IS GENERATING SUBIMAGES. IS IT CALCULATING THE FEATURES?
    def fit(self) -> bool:
        if self.fc is None or self.fc is False:
            return False

        self.features_positive_array = self.compute_features(self.positive_training_folder)
        self.features_negative_array = self.compute_features(self.negative_training_folder)

        self.train()
        self.hard_negative_mining()

        return True

    def hard_negative_mining(self) -> bool:
        if self.fc is None or self.fc is False:
            return False

        new_negative_features: numpy.ndarray = None

        thefiles = os.listdir(self.hard_negative_training_folder)

        for f in thefiles:
            # If it is not a directory, read the image, calculate the hog features and append to a list.
            # (this is apparently faster than appending to an ndarray:
            # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

            thepath = os.path.join(self.hard_negative_training_folder, f)

            if os.path.isfile(thepath):
                # Read the file as an image.
                image = rimutils.read_stack(thepath)
                image = numpy.squeeze(image)

                subimages = rimutils.generate_subimages(image, self.train_image_size, self.step_sz)

                for subim in subimages:
                    # At each window, extract features.
                    self.fc.calculate_features(subim[0])

                    # Apply classifier.
                    imfeatures: numpy.ndarray = self.fc.gimme_features()
                    theclass = self.classifier.predict(imfeatures)

                    # If classifier (incorrectly) classifies a given image as an object, add feature vector to negative
                    # training set.
                    if theclass == 1:
                        if new_negative_features is None:
                            new_negative_features = imfeatures
                        else:
                            new_negative_features = numpy.vstack((new_negative_features, imfeatures))

        # Re-train your classifier using hard-negative samples as well.
        self.features_negative_array = numpy.vstack((self.features_negative_array, new_negative_features))

        self.train()

    def train(self) -> bool:
        if self.features_positive_array is False or self.features_positive_array is None or \
                self.features_negative_array is False or self.features_negative_array is None:
            return False

        features_combined = numpy.vstack((self.features_positive_array, self.features_negative_array))
        class_combined = numpy.concatenate((numpy.ones((self.features_positive_array.shape[0],), dtype=int),
                                            -1 * numpy.ones((self.features_negative_array.shape[0],), dtype=int)))

        # Train using Platt scaling to generate probabilities in addition to classes (https://stackoverflow.com/questions/15111408/how-does-sklearn-svm-svcs-function-predict-proba-work-internally)
        self.classifier.fit(features_combined, class_combined)
        return True

    # Could this method be in rimclassifier? it uses predict and predict_proba.
    # Can create a batch_find method that loops over this one.
    def predict(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):  # rename to predict to stay consistent with scikit-learn?
        if self.fc is None or self.fc is False or image is None or image is False:
            return False

        image = numpy.squeeze(image)

        row_rad = int(numpy.floor(self.train_image_size[0] / 2))
        col_rad = int(numpy.floor(self.train_image_size[1] / 2))

        self.object_positions: list = []
        self.object_map: numpy.ndarray = numpy.zeros(image.shape)
        box_list: list = []
        prob_list: list = []

        subimages = rimutils.generate_subimages(image, self.train_image_size, self.step_sz)

        for subim, row, col in subimages:
            # At each window, extract HOG descriptors.
            self.fc.calculate_features(subim)

            # Apply the classifier.
            theclass = self.classifier.predict(self.fc.gimme_features())
            theP = self.classifier.predict_proba(self.fc.gimme_features())

            # If there is an object, store the position of the bounding box.
            if theclass == 1:
                minrow = row - row_rad
                maxrow = row + row_rad
                if self.train_image_size[0] % 2 == 1:
                    maxrow += 1

                mincol = col - col_rad
                maxcol = col + col_rad
                if self.train_image_size[1] % 2 == 1:
                    maxcol += 1

                self.object_positions.append([row, col])
                self.object_map[row, col] = 1
                box_list.append([minrow, mincol, maxrow,
                                 maxcol])  # this is the right order for tensorflow. Before, we used to use [mincol, minrow, maxcol, maxrow]
                prob_list.append(theP[0][1])  # theP[0][0] contains the probability of the other class (-1)

        self.box_array = numpy.asarray(box_list)
        self.prob_array = numpy.asarray(prob_list)

        return self.box_array.copy(), self.prob_array.copy()

    def save_classifier(self, filename: str) -> bool:
        theclassifier = {
            'positive_training_folder': self.positive_training_folder,
            'negative_training_folder': self.negative_training_folder,
            'hard_negative_training_folder': self.hard_negative_training_folder,
            'train_image_size': self.train_image_size,
            'fc': self.fc,
            'step_sz': self.step_sz,
            'C': self.misclass_penalty_C,
            'kernel_type': self.kernel_type,
            'iou_threshold': self.iou_threshold,
            'prob_threshold': self.prob_threshold,
            'max_num_objects_dial': self.max_num_objects,
            'classifier': self.classifier,
            'features_positive_array': self.features_positive_array,
            'features_negative_array': self.features_negative_array,
        }

        if filename[-4:] != rimclassifier.CLASSIFIER_EXTENSION:
            filename = filename + rimclassifier.CLASSIFIER_EXTENSION


        # Open file for writing.
        fh = None

        try:
            fh = gzip.open(filename, "wb")
            pickle.dump(theclassifier, fh, pickle.HIGHEST_PROTOCOL)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False

        return True
