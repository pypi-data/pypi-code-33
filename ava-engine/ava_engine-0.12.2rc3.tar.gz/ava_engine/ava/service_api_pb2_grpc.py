# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from ava_engine.ava import engine_api_pb2 as ava__engine_dot_ava_dot_engine__api__pb2
from ava_engine.ava import feature_classification_pb2 as ava__engine_dot_ava_dot_feature__classification__pb2
from ava_engine.ava import feature_detection_pb2 as ava__engine_dot_ava_dot_feature__detection__pb2
from ava_engine.ava import feature_face_recognition_pb2 as ava__engine_dot_ava_dot_feature__face__recognition__pb2
from ava_engine.ava import images_api_pb2 as ava__engine_dot_ava_dot_images__api__pb2


class EngineApiDefStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Status = channel.unary_unary(
        '/ava_engine.EngineApiDef/Status',
        request_serializer=ava__engine_dot_ava_dot_engine__api__pb2.StatusRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_engine__api__pb2.StatusResponse.FromString,
        )
    self.PerformanceTest = channel.unary_unary(
        '/ava_engine.EngineApiDef/PerformanceTest',
        request_serializer=ava__engine_dot_ava_dot_engine__api__pb2.PerformanceTestRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_engine__api__pb2.PerformanceTestResponse.FromString,
        )


class EngineApiDefServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Status(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def PerformanceTest(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_EngineApiDefServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Status': grpc.unary_unary_rpc_method_handler(
          servicer.Status,
          request_deserializer=ava__engine_dot_ava_dot_engine__api__pb2.StatusRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_engine__api__pb2.StatusResponse.SerializeToString,
      ),
      'PerformanceTest': grpc.unary_unary_rpc_method_handler(
          servicer.PerformanceTest,
          request_deserializer=ava__engine_dot_ava_dot_engine__api__pb2.PerformanceTestRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_engine__api__pb2.PerformanceTestResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'ava_engine.EngineApiDef', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class ImagesApiDefStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetImage = channel.unary_unary(
        '/ava_engine.ImagesApiDef/GetImage',
        request_serializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageResponse.FromString,
        )
    self.GetImageBytes = channel.unary_unary(
        '/ava_engine.ImagesApiDef/GetImageBytes',
        request_serializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageBytesResponse.FromString,
        )
    self.SearchImages = channel.unary_unary(
        '/ava_engine.ImagesApiDef/SearchImages',
        request_serializer=ava__engine_dot_ava_dot_images__api__pb2.SearchImagesRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_images__api__pb2.SearchImagesResponse.FromString,
        )


class ImagesApiDefServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetImage(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetImageBytes(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SearchImages(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ImagesApiDefServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetImage': grpc.unary_unary_rpc_method_handler(
          servicer.GetImage,
          request_deserializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageResponse.SerializeToString,
      ),
      'GetImageBytes': grpc.unary_unary_rpc_method_handler(
          servicer.GetImageBytes,
          request_deserializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_images__api__pb2.GetImageBytesResponse.SerializeToString,
      ),
      'SearchImages': grpc.unary_unary_rpc_method_handler(
          servicer.SearchImages,
          request_deserializer=ava__engine_dot_ava_dot_images__api__pb2.SearchImagesRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_images__api__pb2.SearchImagesResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'ava_engine.ImagesApiDef', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class ClassificationApiDefStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Detect = channel.unary_unary(
        '/ava_engine.ClassificationApiDef/Detect',
        request_serializer=ava__engine_dot_ava_dot_feature__classification__pb2.ClassifyRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_feature__classification__pb2.ClassifyResponse.FromString,
        )


class ClassificationApiDefServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Detect(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ClassificationApiDefServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Detect': grpc.unary_unary_rpc_method_handler(
          servicer.Detect,
          request_deserializer=ava__engine_dot_ava_dot_feature__classification__pb2.ClassifyRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_feature__classification__pb2.ClassifyResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'ava_engine.ClassificationApiDef', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class DetectionApiDefStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Detect = channel.unary_unary(
        '/ava_engine.DetectionApiDef/Detect',
        request_serializer=ava__engine_dot_ava_dot_feature__detection__pb2.DetectRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_feature__detection__pb2.DetectResponse.FromString,
        )


class DetectionApiDefServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Detect(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DetectionApiDefServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Detect': grpc.unary_unary_rpc_method_handler(
          servicer.Detect,
          request_deserializer=ava__engine_dot_ava_dot_feature__detection__pb2.DetectRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_feature__detection__pb2.DetectResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'ava_engine.DetectionApiDef', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class FaceRecognitionApiDefStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Recognize = channel.unary_unary(
        '/ava_engine.FaceRecognitionApiDef/Recognize',
        request_serializer=ava__engine_dot_ava_dot_feature__face__recognition__pb2.RecognizeFaceRequest.SerializeToString,
        response_deserializer=ava__engine_dot_ava_dot_feature__face__recognition__pb2.RecognizeFaceResponse.FromString,
        )


class FaceRecognitionApiDefServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Recognize(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_FaceRecognitionApiDefServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Recognize': grpc.unary_unary_rpc_method_handler(
          servicer.Recognize,
          request_deserializer=ava__engine_dot_ava_dot_feature__face__recognition__pb2.RecognizeFaceRequest.FromString,
          response_serializer=ava__engine_dot_ava_dot_feature__face__recognition__pb2.RecognizeFaceResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'ava_engine.FaceRecognitionApiDef', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
