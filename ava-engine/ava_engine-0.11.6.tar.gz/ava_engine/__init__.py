#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

from ava_engine.ava.engine_api_pb2 import Features, StatusRequest
from ava_engine.ava.engine_core_pb2 import BoundingBox, SAVE_ALL, SAVE_NOTHING, SAVE_RESULT, ExclusionZone, Point

from ava_engine.ava.images_api_pb2 import GetImageRequest, SearchImagesRequest
from ava_engine.ava.feature_classification_pb2 import ClassifyRequest
from ava_engine.ava.feature_detection_pb2 import DetectRequest
from ava_engine.ava.feature_face_recognition_pb2 import \
    AddFaceRequest, \
    GetFaceRequest, \
    ListFacesRequest, \
    AddIdentityRequest, \
    GetIdentityRequest, \
    UpdateIdentityRequest, \
    RemoveIdentityRequest, \
    ListIdentitiesRequest, \
    RecognizeFaceRequest, \
    ComputeClusterSetRequest, \
    GetClusterSetRequest, \
    ListClusterSetsRequest

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

    def add_face(self, group_id, face_thumbnails):
        return self._stub.AddFace(AddFaceRequest(group_id=group_id, faces=face_thumbnails))

    def get_face(self, face_id):
        return self._stub.GetFace(GetFaceRequest(face_id=face_id))

    def list_faces(self, group_id, start = 0, end = 0, limit = 100, min_width = 0, min_height = 0, min_sharpness = 0, frontal_pose=None):
        return self._stub.ListFaces(ListFacesRequest(
            group_id=group_id,
            start=start,
            end=end,
            limit=limit,
            min_width=min_width,
            min_height=min_height,
            min_sharpness=min_sharpness,
            frontal_pose=frontal_pose,
        ))

    def add_identity(self, identity):
        return self._stub.AddIdentity(AddIdentityRequest(
            group_id=identity.get('group_id'),
            name=identity.get('name'),
            custom_id=identity.get('custom_id', ''),
            face_ids=identity.get('face_ids'),
            cover_image=identity.get('cover_image', ''),
        ))
    
    def get_identity(self, identity_id):
        return self._stub.GetIdentity(GetIdentityRequest(id=identity_id))

    def update_identity(self, update):
        return self._stub.UpdateIdentity(UpdateIdentityRequest(
            id=update.get('id'),
            name=update.get('name'),
            custom_id=update.get('custom_id', ''),
            add_face_ids=update.get('add_face_ids'),
            remove_face_ids=update.get('remove_face_ids'),
            cover_image=update.get('cover_image', ''),
        ))

    def remove_identity(self, identity_id):
        return self._stub.RemoveIdentity(RemoveIdentityRequest(
            id=identity_id
        ))

    def list_identities(self, group_id, custom_id=''):
        return self._stub.ListIdentities(ListIdentitiesRequest(group_id=group_id, custom_id=custom_id))

    def recognize(self, images, persistence):
        return self._stub.Recognize(RecognizeFaceRequest(
            images=images,
            persistence=persistence
        ))

    def compute_cluster_set(self, group_id, face_ids, custom_id=''):
        return self._stub.ComputeClusterSet(ComputeClusterSetRequest(
            group_id=group_id,
            custom_id=custom_id,
            face_ids=face_ids,
        ))

    def get_cluster_set(self, id):
        return self._stub.GetClusterSet(GetClusterSetRequest(id=id))

    def list_cluster_sets(self, group_id, custom_id='', start = 0, end = 0, limit = 10):
        return self._stub.ListClusterSets(ListClusterSetsRequest(
          group_id=group_id, 
          custom_id=custom_id, 
          start=start, 
          end=end, 
          limit=limit,
        ))

    def remove_cluster_set(self, id):
        return self._stub.RemoveClusterSet(RemoveClusterSetRequest(id=id))

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
