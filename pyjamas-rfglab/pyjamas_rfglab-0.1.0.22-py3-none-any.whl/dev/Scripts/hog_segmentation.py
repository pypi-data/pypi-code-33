"""
@todo:
- Try to train not on the basis of image features, but pixel ones, to classify the pixels as object or not.

Done:
    - Changed non-max supression to use prob_list (https://www.coursera.org/lecture/convolutional-neural-networks/non-max-suppression-dvrjH)

"""

from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.patches as ptch
from matplotlib.colors import ListedColormap
from skimage.feature import hog
from skimage import data, exposure, io
import numpy
import os, os.path
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import tensorflow as tf
from tensorflow import image as tfimage
from PIL.Image import fromarray

# Where to find the training images and those to be segmented.
positive_training_folder = '/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/training/positive'
negative_training_folder = '/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/training/negative'
hard_negative_training_folder = '/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/training/hard_negative'
test_folder = '/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/test'

# Parameters for skimage.feature.hog
orientations = 8
pixels_per_cell = (8, 8)
cells_per_block = (2, 2)
block_norm = 'L2'

# SVM params
misclass_penalty_C = 1.0  # small values (0.05) result in some additional nuclei detected and others not.
# large values (100) do not seem to change the result with respect to 1.0.
kernel_type = 'linear'

# Tree params
tree_max_depth = 4


# Possible types of classifier.
class ClassifierType(Enum):
    SVM = 'svm'
    TREE = 'tree'


classifier_type = ClassifierType.SVM

# Scanning params.
step_sz = 5  # For SVM at least, when this parameter equals 1 more objects are recognized than when it equals 5.

# Non-max suppression params.
iou_threshold = .325  # When iou_threshold (intersection/union) is small, fewer boxes are left, as boxes with overlap
# above the threshold are suppressed.
prob_threshold = .95
# Initialize tensorflow (used for non-max suppression).
tf.InteractiveSession()


train_image_size = (46, 41)  # (rows, cols)

features_positive = []
features_negative = []


# List files in the positive training folder.
thefiles = os.listdir(positive_training_folder)

# For each file:
for f in thefiles:

    # If it is not a directory, read the image, calculate the hog features and append to a list.
    # (this is apparently faster than appending to an ndarray:
    # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

    thepath = os.path.join(positive_training_folder, f)

    if os.path.isfile(thepath):
        # Read the file as an image. @todo: this may throw an exception.
        image = io.imread(thepath)
        image = numpy.squeeze(image)

        # Calculate hog features and append to the list.
        features_positive.append(
            hog(image, orientations=orientations, pixels_per_cell=pixels_per_cell, cells_per_block=cells_per_block,
                visualize=False, block_norm=block_norm))

features_positive_array = numpy.asarray(features_positive)  # Asarray does NOT copy the data (if possible).

# List files in the negative training folder.
thefiles = os.listdir(negative_training_folder)

# For each file:
for f in thefiles:

    # If it is not a directory, read the image, calculate the hog features and append to a list.
    # (this is apparently faster than appending to an ndarray:
    # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

    thepath = os.path.join(negative_training_folder, f)

    if os.path.isfile(thepath):
        # Read the file as an image. @todo: this may throw an exception.
        image = io.imread(thepath)
        image = numpy.squeeze(image)

        # Calculate hog features and append to the list.
        features_negative.append(
            hog(image, orientations=orientations, pixels_per_cell=pixels_per_cell, cells_per_block=cells_per_block,
                visualize=False, block_norm=block_norm))

features_negative_array = numpy.asarray(features_negative)  # Asarray does NOT copy the data (if possible).

features_combined = numpy.vstack((features_positive_array, features_negative_array))
class_combined = numpy.concatenate((numpy.ones((features_positive_array.shape[0],), dtype=int),
                                    -1 * numpy.ones((features_negative_array.shape[0],), dtype=int)))

if classifier_type == ClassifierType.SVM:
    # Train using Platt scaling to generate probabilities in addition to classes (https://stackoverflow.com/questions/15111408/how-does-sklearn-svm-svcs-function-predict-proba-work-internally)
    svm = SVC(kernel=kernel_type, C=misclass_penalty_C, random_state=1, probability=True)
    svm.fit(features_combined, class_combined)
elif classifier_type == ClassifierType.TREE:
    # Train a decision tree.
    tree = DecisionTreeClassifier(criterion='gini', max_depth=tree_max_depth, random_state=1)
    tree.fit(features_combined, class_combined)

# HARD-NEGATIVE MINING -------------------------------------------------------------------------------------------------.
# List files in the hard-negative training folder.
thefiles = os.listdir(hard_negative_training_folder)

# For each file:
for f in thefiles:

    # If it is not a directory, read the image, calculate the hog features and append to a list.
    # (this is apparently faster than appending to an ndarray:
    # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

    thepath = os.path.join(hard_negative_training_folder, f)

    numim = 0

    if os.path.isfile(thepath):
        # Read the file as an image. @todo: this may throw an exception.
        image = io.imread(thepath)
        image = numpy.squeeze(image)

        # First, apply the sliding window technique
        row_rad = int(numpy.floor(train_image_size[0] / 2))
        col_rad = int(numpy.floor(train_image_size[1] / 2))
        max_row_range = image.shape[0] - row_rad
        if train_image_size[0] % 2 == 0:
            max_row_range += 1
        max_col_range = image.shape[1] - col_rad
        if train_image_size[1] % 2 == 0:
            max_col_range += 1

        for row in range(row_rad, max_row_range, step_sz):
            for col in range(col_rad, max_col_range, step_sz):
                minrow = row - row_rad
                maxrow = row + row_rad
                if train_image_size[0] % 2 == 1:
                    maxrow += 1

                mincol = col - col_rad
                maxcol = col + col_rad
                if train_image_size[1] % 2 == 1:
                    maxcol += 1

                subim = image[minrow:maxrow, mincol:maxcol]
                numim += 1

                # At each window, extract HOG descriptors.
                features = hog(subim, orientations=orientations, pixels_per_cell=pixels_per_cell,
                               cells_per_block=cells_per_block,
                               visualize=False, block_norm=block_norm)

                # Apply classifier.
                if classifier_type == ClassifierType.SVM:
                    theclass = svm.predict(numpy.expand_dims(features, axis=0))
                    theP = svm.predict_proba(numpy.expand_dims(features, axis=0))
                elif classifier_type == ClassifierType.TREE:
                    theclass = tree.predict(numpy.expand_dims(features, axis=0))
                    theP = tree.predict_proba(numpy.expand_dims(features, axis=0))

                # If classifier (incorrectly) classifies a given image as an object, add feature vector to negative
                # training set.
                if theclass == 1:
                    features_negative.append(features)

# Re-train your classifier using hard-negative samples as well.
features_negative_array = numpy.asarray(features_negative)  # Asarray does NOT copy the data (if possible).

features_combined = numpy.vstack((features_positive_array, features_negative_array))
class_combined = numpy.concatenate((numpy.ones((features_positive_array.shape[0],), dtype=int),
                                    -1 * numpy.ones((features_negative_array.shape[0],), dtype=int)))

if classifier_type == ClassifierType.SVM:
    # Train using Platt scaling to generate probabilities in addition to classes (https://stackoverflow.com/questions/15111408/how-does-sklearn-svm-svcs-function-predict-proba-work-internally)
    svm = SVC(kernel=kernel_type, C=misclass_penalty_C, random_state=1, probability=True)
    svm.fit(features_combined, class_combined)

elif classifier_type == ClassifierType.TREE:
    # Train a decision tree.
    tree = DecisionTreeClassifier(criterion='gini', max_depth=tree_max_depth, random_state=1)
    tree.fit(features_combined, class_combined)

# END HARD NEGATIVE MINING ---------------------------------------------------------------------------------------------

# Now look for objects in the test images.
thefiles = os.listdir(test_folder)

# For each file:
for f in thefiles:

    # If it is not a directory, read the image, calculate the hog features and append to a list.
    # (this is apparently faster than appending to an ndarray:
    # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

    thepath = os.path.join(test_folder, f)

    if os.path.isfile(thepath):
        # Read the file as an image. @todo: this may throw an exception.
        image = io.imread(thepath)
        image = numpy.squeeze(image)

    object_positions = []
    object_map = numpy.zeros(image.shape)
    box_list = []
    prob_list = []

    # First, apply the sliding window technique
    row_rad = int(numpy.floor(train_image_size[0] / 2))
    col_rad = int(numpy.floor(train_image_size[1] / 2))
    max_row_range = image.shape[0] - row_rad
    if train_image_size[0] % 2 == 0:
        max_row_range += 1
    max_col_range = image.shape[1] - col_rad
    if train_image_size[1] % 2 == 0:
        max_col_range += 1

    for row in range(row_rad, max_row_range, step_sz):
        for col in range(col_rad, max_col_range, step_sz):
            minrow = row - row_rad
            maxrow = row + row_rad
            if train_image_size[0] % 2 == 1:
                maxrow += 1

            mincol = col - col_rad
            maxcol = col + col_rad
            if train_image_size[1] % 2 == 1:
                maxcol += 1

            subim = image[minrow:maxrow, mincol:maxcol]

            # At each window, extract HOG descriptors.
            features = numpy.expand_dims(
                hog(subim, orientations=orientations, pixels_per_cell=pixels_per_cell, cells_per_block=cells_per_block,
                    visualize=False, block_norm=block_norm), axis=0)

            # Apply the classifier.
            if classifier_type == ClassifierType.SVM:
                theclass = svm.predict(features)
                theP = svm.predict_proba(features)
            elif classifier_type == ClassifierType.TREE:
                theclass = tree.predict(features)
                theP = tree.predict_proba(features)

            # If there is an object, store the position of the bounding box.
            if theclass == 1:
                object_positions.append([row, col])
                object_map[row, col] = 1
                box_list.append([minrow, mincol, maxrow,
                                 maxcol])  # this is the right order for tensorflow. Before, we used to use [mincol, minrow, maxcol, maxrow]
                prob_list.append(theP[0][1])  # theP[0][0] contains the probability of the other class (-1)

    # Apply non-maximum suppression to remove redundant and overlapping bounding boxes.
    box_array = numpy.asarray(box_list)
    prob_array = numpy.asarray(prob_list)

    # Trying to use tensorflow here: https://www.tensorflow.org/api_docs/python/tf/image/non_max_suppression
    # Other methods: http://openaccess.thecvf.com/content_cvpr_2017/papers/Hosang_Learning_Non-Maximum_Suppression_CVPR_2017_paper.pdf
    good_box_indices_tensor = tfimage.non_max_suppression(box_array, prob_array, max_output_size=200,
                                                          iou_threshold=iou_threshold,
                                                          score_threshold=prob_threshold)
    good_box_indices = good_box_indices_tensor.eval(session=tf.get_default_session())
    good_box_array = box_array[good_box_indices]

    # For display @todo: use pyqt
    fig, ax = plt.subplots(1, 2)
    ax1 = ax[0]
    ax2 = ax[1]

    ax1.imshow(image, cmap='gray')

#    for i in range(box_array.shape[0]):
#        rect = ptch.Rectangle((box_array[i, 1], box_array[i, 0]), box_array[i, 3] - box_array[i, 1] + 1,
#                              box_array[i, 2] - box_array[i, 0] + 1, linewidth=1, edgecolor='r', facecolor='none')
#        ax1.add_patch(rect)

    ax2.imshow(image, cmap='gray')

    for i in range(good_box_array.shape[0]):
        w = good_box_array[i, 3] - good_box_array[i, 1] + 1
        h = good_box_array[i, 2] - good_box_array[i, 0] + 1

        #rect = ptch.Rectangle((good_box_array[i, 1], good_box_array[i, 0]),
        #                      w,
        #                      h, linewidth=1, edgecolor='r',
        #                      facecolor='none')

        small_rect = ptch.Rectangle((good_box_array[i, 1]+w/4, good_box_array[i, 0]+h/4),
                              w/2,
                              h/2, linewidth=1, edgecolor='r',
                              facecolor='none')
        #circle = ptch.Circle((good_box_array[i, 1] + w / 2.,
        #                      good_box_array[i, 0] + h / 2.), 5)
        ax2.add_patch(small_rect)

    fig1 = plt.gcf()
    plt.show() # savefig will not work after show (it will save a new, blank image).
    fig1.savefig('test.pdf', dpi=300)
    # End display -> use pyqt.

thepath = os.path.join(positive_training_folder, f)

image = io.imread(thepath)
image = numpy.squeeze(image)
fd, hog_image = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=True, block_norm='L2')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), sharex=True, sharey=True)

ax1.axis('off')
ax1.imshow(image, cmap=plt.cm.gray)
ax1.set_title('Input image')

#Rescale histogram for better display
hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, numpy.max(hog_image)))

ax2.axis('off')
ax2.imshow(hog_image_rescaled, cmap=plt.cm.gray)
ax2.set_title('Histogram of Oriented Gradients')
plt.show()

# Plot a single image.
fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
ax.axis('off')
ax.imshow(hog_image_rescaled, cmap=plt.cm.gray)
plt.show()


"""
plot_decision_regions(features_combined, class_combined, classifier=svm)
pplt.xlabel(' petal length [standardized]')
plt.ylabel(' petal width [standardized]')
plt.show()

def plot_decision_regions(X, y, classifier, resolution=0.02):

    # setup marker generator and color map
    markers = ('s', 'x', 'o', '^', 'v')
    colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')
    cmap = ListedColormap(colors[:len(numpy.unique(y))])

    # plot the decision surface
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx1, xx2 = numpy.meshgrid(numpy.arange(x1_min, x1_max, resolution),
                           numpy.arange(x2_min, x2_max, resolution))
    Z = classifier.predict(numpy.array([xx1.ravel(), xx2.ravel()]).T)
    Z = Z.reshape(xx1.shape)
    plt.contourf(xx1, xx2, Z, alpha=0.3, cmap=cmap)
    plt.xlim(xx1.min(), xx1.max())
    plt.ylim(xx2.min(), xx2.max())

    # plot class samples
    for idx, cl in enumerate(numpy.unique(y)):
        plt.scatter(x=X[y == cl, 0], 
                    y=X[y == cl, 1],
                    alpha=0.8, 
                    c=colors[idx],
                    marker=markers[idx], 
                    label=cl, 
                    edgecolor='black')
"""
