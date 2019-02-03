from __future__ import print_function
import os
import random
from shutil import copyfile
from pathlib import Path

from lxml import etree
from eyewitness.config import BBOX, BoundedBoxObject
from eyewitness.image_id import ImageId
from eyewitness.image_utils import Image
from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.models.feedback_models import FalseAlertFeedback
from eyewitness.models.detection_models import BboxDetectionResult
from eyewitness.utils import make_path


def add_filename_prefix(filename, prefix):
    return "%s_%s" % (prefix, filename)


def create_bbox_dataset_from_eyewitness(
        database, valid_classes, output_dataset_folder, dataset_name):
    """
    generate bbox dataset from eyewitness

    - remove images with false-alert feedback

    - get images with selected classes objects
    """
    anno_folder = str(Path(output_dataset_folder, 'Annotations'))
    jpg_images_folder = str(Path(output_dataset_folder, 'JPEGImages'))
    main_folder = str(Path(output_dataset_folder, 'ImageSets', 'Main'))

    # mkdir if not exist
    make_path(anno_folder)
    make_path(jpg_images_folder)
    make_path(main_folder)

    DATABASE_PROXY.initialize(database)
    # filter false alert, and valid_classes
    false_alert_query = FalseAlertFeedback.select(
        FalseAlertFeedback.image_id).where(FalseAlertFeedback.is_false_alert)
    valid_objects = BboxDetectionResult.select().where(
        BboxDetectionResult.image_id.not_in(false_alert_query),
        BboxDetectionResult.label.in_(valid_classes))

    # get valid_images with raw_image_path
    valid_images = set(i.image_id for i in valid_objects if i.image_id.raw_image_path)

    # generate etree obj for each images
    for valid_image in valid_images:
        if (valid_image.file_format != 'jpg' or not os.path.exists(valid_image.raw_image_path)):
            # TODO: support other file_format
            continue

        ori_image_file = valid_image.raw_image_path
        dest_image_file = str(Path(jpg_images_folder, "%s.jpg" % valid_image.image_id))
        copyfile(ori_image_file, dest_image_file)

        # prepare anno_file
        anno_file = str(Path(anno_folder, "%s.xml" % valid_image.image_id))
        detected_objects = list(BboxDetectionResult.select().where(
            BboxDetectionResult.image_id == valid_image,
            BboxDetectionResult.label.in_(valid_classes)))
        if detected_objects:  # make sure there is detected objects
            etree_obj = generate_etree_obj(valid_image.image_id, detected_objects, dataset_name)
            etree_obj.write(anno_file, pretty_print=True)


def generate_etree_obj(image_id, detected_objects, dataset_name):
    """
    Parameters
    ----------
    image_id: str
        image_id as filename
    detected_objects:
        detected_objects obj from detected_objects table
    dataset_name: str
        dataset_name
    """
    root = etree.Element("annotation")
    filename = etree.SubElement(root, "filename")
    source = etree.SubElement(root, "source")
    databases = etree.SubElement(source, "database")

    filename.text = image_id
    databases.text = dataset_name
    for obj in detected_objects:
        object_ = etree.SubElement(root, "object")
        name = etree.SubElement(object_, "name")
        name.text = obj.label
        pose = etree.SubElement(object_, "pose")
        pose.text = "Unspecified"
        truncated = etree.SubElement(object_, "truncated")
        truncated.text = "0"
        difficult = etree.SubElement(object_, "difficult")
        difficult.text = "0"
        # bounded box
        bndbox = etree.SubElement(object_, "bndbox")
        xmin_ = etree.SubElement(bndbox, "xmin")
        ymin_ = etree.SubElement(bndbox, "ymin")
        xmax_ = etree.SubElement(bndbox, "xmax")
        ymax_ = etree.SubElement(bndbox, "ymax")
        xmin_.text = str(obj.x1)
        ymin_.text = str(obj.y1)
        xmax_.text = str(obj.x2)
        ymax_.text = str(obj.y2)
    return etree.ElementTree(root)


def copy_image_to_output_dataset(filename, src_dataset, jpg_images_folder, anno_folder, file_fp):
    """
    move annotation, jpg file from src_dataset to file destination,
    add prefix to filename and print to id list file

    Parameters
    ----------
    filename: str
        ori filename
    src_dataset: BboxDataSet
        source dataset

    jpg_images_folder: str
        destination jpg file folder

    anno_folder: str
        destination annotation file folder

    file_fp:
        the file pointer used to export the id list
    """
    filename_with_prefix = add_filename_prefix(filename, src_dataset.dataset_name)

    # copy image file
    ori_image_file = str(Path(src_dataset.jpg_images_folder, "%s.jpg" % filename))
    dest_image_file = str(Path(jpg_images_folder, "%s.jpg" % filename_with_prefix))
    copyfile(ori_image_file, dest_image_file)

    # copy annotation file
    ori_anno_file = str(Path(src_dataset.anno_folder, "%s.xml" % filename))
    dest_anno_file = str(Path(anno_folder, "%s.xml" % filename_with_prefix))
    copyfile(ori_anno_file, dest_anno_file)

    # print filename to the filename list file
    print(filename_with_prefix, file=file_fp)


def parse_xml_obj(obj):
    label = obj.find('name').text
    x1 = int(obj.find('bndbox').find('xmin').text)
    y1 = int(obj.find('bndbox').find('ymin').text)
    x2 = int(obj.find('bndbox').find('xmax').text)
    y2 = int(obj.find('bndbox').find('ymax').text)
    return BoundedBoxObject(x1, y1, x2, y2, label, 1, '')


class BboxDataSet(object):
    """
    generate DataSet with same format as VOC object detections:

    <dataset_folder>/Annotations/<image_name>.xml

    <dataset_folder>/JPEGImages/<image_name>.jpg

    <dataset_folder>/ImageSets/Main/trainval.txt

    <dataset_folder>/ImageSets/Main/test.txt

    """
    def __init__(self, dataset_folder, dataset_name, valid_labels=None):
        self.anno_folder = str(Path(dataset_folder, 'Annotations'))
        self.jpg_images_folder = str(Path(dataset_folder, 'JPEGImages'))
        self.main_folder = str(Path(dataset_folder, 'ImageSets', 'Main'))
        self.trainval_file = str(Path(self.main_folder, 'trainval.txt'))
        self.test_file = str(Path(self.main_folder, 'test.txt'))
        self.dataset_name = dataset_name
        self._valid_labels = valid_labels

    @property
    def dataset_type(self):
        return BBOX

    @property
    def valid_labels(self):
        """
        the valid_labels in the dataset
        """
        if self._valid_labels is None:
            self._valid_labels = self.get_valid_labels()
        assert len(self._valid_labels) > 0
        return self._valid_labels

    @property
    def training_and_validation_set(self):
        with open(self.trainval_file) as f:
            for i in f:
                yield i.strip()

    @property
    def testing_set(self):
        with open(self.test_file) as f:
            for i in f:
                yield i.strip()

    def generate_train_test_list(self, overwrite=True, train_ratio=0.9):
        """generate train and test list

        Parameters
        ----------
            overwrite: bool
                if overwrite and file not exit will regenerate the train, test list
            train_ratio: float
                the ratio used to sample train, test list, should between 0~1
        """
        if not overwrite and os.path.exists(self.trainval_file) and os.path.exists(self.test_file):
            return
        else:
            anno_files = Path(self.anno_folder).glob('*.xml')
            image_ids_anno = set(
                str(anno_file).rsplit('/', 1)[1].replace('.xml', '') for anno_file in anno_files)
            jpg_files = Path(self.jpg_images_folder).glob('*.jpg')
            image_ids_jpg = set(
                str(jpg_file).rsplit('/', 1)[1].replace('.jpg', '') for jpg_file in jpg_files)
            image_ids = image_ids_jpg.intersection(image_ids_anno)

            # write to training set
            training_set = random.sample(image_ids, int(len(image_ids) * train_ratio))
            with open(self.trainval_file, 'w') as f:
                for train_id in training_set:
                    print(train_id, file=f)

            testing_set = image_ids.difference(training_set)
            with open(self.test_file, 'w') as f:
                for test_id in testing_set:
                    print(test_id, file=f)

    def get_valid_labels(self):
        valid_labels = set()
        xml_files = Path(self.anno_folder).glob('*.xml')
        for xml_file in xml_files:
            x = etree.parse(str(xml_file))
            gt_objects = x.findall('object')
            labels = [parse_xml_obj(gt_object).label for gt_object in gt_objects]
            valid_labels.update(labels)
        return valid_labels

    def image_obj_iterator(self, testing_set_only=True):
        """
        generate eyewitness Image obj from dataset

        Parameters
        ----------
        testing_set_only: bool
            only iterate testing set or not

        Returns
        -------
        image_obj_generator: Generator[eyewitness.image_utils.Image]
            eyewitness Image obj generator
        """
        selected_images = list(self.testing_set)
        if not testing_set_only:
            selected_images.extend(self.training_and_validation_set)
        for selected_image in selected_images:
            # TODO: design better representation for ImageId
            image_id = ImageId(selected_image, 0, 'jpg')
            jpg_file = str(Path(self.jpg_images_folder, '%s.jpg' % selected_image))
            yield Image(image_id, raw_image_path=jpg_file)

    def ground_truth_iterator(self, testing_set_only=True):
        """
        ground_truth interator

        Parameters
        ----------
        testing_set_only: bool
            only iterate testing set or not

        Returns
        -------
        gt_object_generator: Generator[(ImageId, List[BoundedBoxObject])]
            ground_truth_object generator, with first item if the ImageId
        """
        selected_images = list(self.testing_set)
        if not testing_set_only:
            selected_images.extend(self.training_and_validation_set)
        for selected_image in selected_images:
            # TODO: design better representation for ImageId
            image_id = ImageId(selected_image, 0, 'jpg')
            xml_file = str(Path(self.anno_folder, '%s.xml' % (selected_image)))
            x = etree.parse(xml_file)
            gt_objects = [parse_xml_obj(gt_object) for gt_object in x.findall('object')]
            yield (image_id, gt_objects)

    @classmethod
    def union_bbox_datasets(cls, datasets, output_dataset_folder, dataset_name):
        """
        union bbox datasets and copy files to the given output_dataset
        """
        assert all(dataset.dataset_type == BBOX for dataset in datasets)

        anno_folder = str(Path(output_dataset_folder, 'Annotations'))
        jpg_images_folder = str(Path(output_dataset_folder, 'JPEGImages'))
        main_folder = str(Path(output_dataset_folder, 'ImageSets', 'Main'))

        # mkdir if not exist
        make_path(anno_folder)
        make_path(jpg_images_folder)
        make_path(main_folder)

        # write train, test list out
        trainval_file = str(Path(main_folder, 'trainval.txt'))
        test_file = str(Path(main_folder, 'test.txt'))
        with open(trainval_file, 'w') as train_fp, open(test_file, 'w') as test_fp:
            for dataset in datasets:
                for train_file in dataset.training_and_validation_set:
                    copy_image_to_output_dataset(
                        train_file, dataset, jpg_images_folder, anno_folder, train_fp)

                for test_file in dataset.testing_set:
                    copy_image_to_output_dataset(
                        test_file, dataset, jpg_images_folder, anno_folder, test_fp)

        return cls(output_dataset_folder, dataset_name)
