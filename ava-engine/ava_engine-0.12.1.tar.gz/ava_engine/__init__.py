#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

from ava_engine.ava.engine_api_pb2 import Features, StatusRequest
from ava_engine.ava.engine_core_pb2 import SAVE_ALL, SAVE_NOTHING, SAVE_RESULT, ExclusionZone, Point

from ava_engine.ava.images_api_pb2 import GetImageRequest, SearchImagesRequest
from ava_engine.ava.feature_classification_pb2 import ClassifyRequest
from ava_engine.ava.feature_detection_pb2 import DetectRequest
from ava_engine.ava.feature_face_recognition_pb2 import RecognizeFaceRequest
   

from ava_engine.ava.engine_core_pb2 import ImageItem
from ava_engine.ava.service_api_pb2_grpc import EngineApiDefStub, \
    ClassificationApiDefStub, DetectionApiDefStub, FaceRecognitionApiDefStub, ImagesApiDefStub


class _ClassificationFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ClassificationApiDefStub(self._channel)

    def detect(self, images, classes, persistence):
        return self._stub.Detect(ClassifyRequest(
            images=images, 
            classes=classes, 
            persistence=persistence
        ))

class _DetectionFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = DetectionApiDefStub(self._channel)

    def detect(self, images, persistence):
        return self._stub.Detect(DetectRequest(
            images=images, 
            persistence=persistence
        ))


class _FaceRecognitionFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = FaceRecognitionApiDefStub(self._channel)

    def recognize(self, images, persistence):
        return self._stub.Recognize(RecognizeFaceRequest(
            images=images,
            persistence=persistence
        ))

class _Images:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ImagesApiDefStub(self._channel)

    def get(self, image_id, feed_id):
        return self._stub.GetImage(GetImageRequest(id=image_id, feed_id=feed_id))

    def getBytes(self, image_id, feed_id):
        return self._stub.GetImageBytes(GetImageRequest(id=image_id, feed_id=feed_id))

    def search(self, options):
        req = SearchImagesRequest(
            start=options.get('start'),
            end=options.get('end'),
            custom_id=options.get('custom_id'),
            feed_ids=options.get('feed_ids'),
            limit=options.get('limit'),
            offset=options.get('offset'),
            query=options.get('query'),
            is_summary=options.get('is_summary'),
        )
        return self._stub.SearchImages(req)


class AvaEngineClient:
    def __init__(self, host='localhost', port=50051):
        self._host = host
        self._port = port

        self._channel = grpc.insecure_channel('{host}:{port}'.format(host=host, port=port))
        self._stub = EngineApiDefStub(self._channel)

        self.classification = _ClassificationFeature(self._channel)
        self.detection = _DetectionFeature(self._channel)
        self.face_recognition = _FaceRecognitionFeature(self._channel)
        self._images = _Images(self._channel)

    @property
    def images(self):
        return self._images

    def status(self):
        return self._stub.Status(StatusRequest())
