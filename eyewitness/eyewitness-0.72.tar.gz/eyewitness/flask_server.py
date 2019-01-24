import io
from collections import defaultdict

import flask_admin
import logging
import arrow
from flask import Flask
from flask import request
from flask_admin.contrib.peewee import ModelView
from eyewitness.image_id import ImageId
from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.models.detection_models import (ImageInfo, BboxDetectionResult)
from eyewitness.models.feedback_models import FalseAlertFeedback
from eyewitness.image_utils import ImageHandler, Image
from eyewitness.config import (
    BoundedBoxObject,
    DETECTED_OBJECTS,
    DRAWN_IMAGE_PATH,
    RAW_IMAGE_PATH,
    IMAGE_ID,
)
from eyewitness.utils import bbox_intersection_over_union


class BboxObjectDetectionFlaskWrapper(object):
    def __init__(self, obj_detector, image_register, detection_result_handlers,
                 database, detection_threshold=0.5, with_admin=False, drawn_image_dir=None,
                 collect_feedback_period=None):
        logging.basicConfig()
        self.logger = logging.getLogger('EyeWitness Flask')
        app = Flask(__name__)
        self.app = app
        self.obj_detector = obj_detector
        self.detection_result_handlers = detection_result_handlers
        self.database = database
        self.image_register = image_register
        self.drawn_image_dir = drawn_image_dir

        # collect_feedback_period, used for de-noise
        self.detection_threshold = detection_threshold
        self.collect_feedback_period = collect_feedback_period
        self.collect_feedback_water_mark = 0
        self.false_alert_feedback_bbox = {}

        DATABASE_PROXY.initialize(self.database)
        ImageInfo.create_table()
        BboxDetectionResult.create_table()
        FalseAlertFeedback.create_table()

        if with_admin:
            admin = flask_admin.Admin(app, name='Example: Peewee')
            admin.add_view(ModelView(ImageInfo))
            admin.add_view(ModelView(BboxDetectionResult))

        @app.route("/detect_post_bytes", methods=['POST'])
        def detect_image_bytes_objs():
            image_id = ImageId.from_str(request.headers[IMAGE_ID])
            raw_image_path = request.headers.get(RAW_IMAGE_PATH)
            self.image_register.register_image(image_id, {RAW_IMAGE_PATH: raw_image_path})

            # read data from Bytes
            data = request.data
            image_data_raw = io.BytesIO(bytearray(data))
            image_raw = ImageHandler.read_image_bytes(image_data_raw)

            if raw_image_path:
                ImageHandler.save(image_raw, raw_image_path)

            image_obj = Image(image_id, pil_image_obj=image_raw)
            # detect objs
            detection_result = self.obj_detector.detect(image_obj)

            # draw and save image, as object detected update detection result
            if self.drawn_image_dir and len(detection_result.detected_objects) > 0:
                self.draw_bbox_for_detection_result(image_obj, detection_result)

            for detection_result_handler in self.detection_result_handlers:
                detection_result_handler.handle(detection_result)
            return "successfully detected"

        @app.route("/detect_post_path", methods=['POST'])
        def detect_image_file_objs():
            image_id = ImageId.from_str(request.headers[IMAGE_ID])
            raw_image_path = request.headers[RAW_IMAGE_PATH]
            self.image_register.register_image(image_id, {RAW_IMAGE_PATH: raw_image_path})

            image_obj = Image(image_id, raw_image_path=raw_image_path)
            detection_result = self.obj_detector.detect(image_obj)

            if self.collect_feedback_period is not None:
                self.bbox_denoise_with_false_alert_msg(detection_result, self.detection_threshold)

            # draw and save image, as object detected update detection result
            if self.drawn_image_dir and len(detection_result.detected_objects) > 0:
                self.draw_bbox_for_detection_result(image_obj, detection_result)

            for detection_result_handler in self.detection_result_handlers:
                detection_result_handler.handle(detection_result)
            return "successfully detected"

    def draw_bbox_for_detection_result(self, image_obj, detection_result):
        """ write the detected_result image to <drawn_dr>/<channel>::<timestamp>.<file_format>

        Parameters
        ----------
        image_obj: eyewitness.image_util.Image
            eyewitness image obj
        detection_result: DetectionResult
            detection result
        """
        drawn_image_path = "%s/%s::%s.%s" % (
            self.drawn_image_dir, image_obj.image_id.channel, image_obj.image_id.timestamp,
            image_obj.image_id.file_format)
        ImageHandler.draw_bbox(image_obj.pil_image_obj, detection_result.detected_objects)
        ImageHandler.save(image_obj.pil_image_obj, drawn_image_path)
        detection_result.image_dict[DRAWN_IMAGE_PATH] = drawn_image_path

    def bbox_denoise_with_false_alert_msg(
            self, detection_result, detection_threshold, decay=0.9, iou_threshold=0.7):
        """
        using the false-alert feedback msgs to de-noise the detection result

        loop over false-alert objects related to (channel, classes),
        if any detected object matched false alert object with iou > iou_threshold:
            `object_score *= decay`

        # TODO: this method is fucking ugly
        """
        # try to collect latest false alert feedback
        self.update_false_alert_feedback_bbox()

        # verify if all detected objs having enough confidence.
        passed_objs = []
        channel = detection_result.image_id.channel
        detected_objs = detection_result.image_dict.get(DETECTED_OBJECTS, [])
        for detected_obj in detected_objs:
            (x1, y1, x2, y2, label, score, meta) = detected_obj
            bbox = (x1, y1, x2, y2)

            # loop over false_alert obj, decay the matched obj score
            false_alert_objs = self.false_alert_feedback_bbox.get((channel, label), [])
            for feedback_obj_bbox in false_alert_objs:
                if bbox_intersection_over_union(bbox, feedback_obj_bbox) > iou_threshold:
                    score *= decay
                    # TODO: meta should be a more flexible way
                    meta += 'decay_%s |' % (decay)

            if score > detection_threshold:
                passed_objs.append(BoundedBoxObject(x1, y1, x2, y2, label, score, meta))
        self.logger.info('original: %s objs, filtered: %s objs',
                         len(detected_objs), len(passed_objs))
        detection_result.image_dict[DETECTED_OBJECTS] = passed_objs

    def update_false_alert_feedback_bbox(self):
        """
        collect_bbox_false_alert_information

        for every period self.collect_feedback_period * 0.005 seconds

        # TODO: this method is fucking ugly
        """
        if self.collect_feedback_period is None:
            self.logger.info('not need feedback info')
            return

        # TODO: make the varables more clear.
        now_timestamp = arrow.now().timestamp
        time_check = self.collect_feedback_water_mark + self.collect_feedback_period * 0.005
        obj_acc = 0
        if (now_timestamp > time_check):
            self.logger.info('collecting latest false alert feedback')
            self.collect_feedback_water_mark = arrow.now().timestamp
            start_time = now_timestamp - self.collect_feedback_period
            query = FalseAlertFeedback.select().where(FalseAlertFeedback.receive_time > start_time)
            feedback_dict = defaultdict(list)
            for feedback in query:
                image_id = feedback.image_id
                channel = image_id.channel
                detected_objs = list(
                    BboxDetectionResult.select().where(BboxDetectionResult.image_id == image_id))
                for obj in detected_objs:
                    label = obj.label
                    bbox = (obj.x1, obj.y1, obj.x2, obj.y2)
                    feedback_dict[(channel, label)].append(bbox)
                    obj_acc += 1
            self.logger.info('collected %s objs', obj_acc)
            self.false_alert_feedback_bbox = feedback_dict
