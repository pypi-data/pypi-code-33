from core.exception.EnvisionException import EnvisionException

class DecoderRegistry(object):

    packages = {
        'message.upstream.status.SubDeviceLoginResponse': 'SubDeviceLoginResponse',
        'message.upstream.topo.TopoAddResponse': 'TopoAddResponse',
        'message.upstream.topo.TopoGetResponse': 'TopoGetResponse',
        'message.upstream.topo.TopoDeleteResponse': 'TopoDeleteResponse',
        'message.upstream.tsl.MeasurepointPostResponse': 'MeasurepointPostResponse',
        'message.downstream.tsl.MeasurepointSetCommand': 'MeasurepointSetCommand'
    }

    @classmethod
    def getDecode(cls, message):
        try:
            for package in cls.packages.items():
                model = __import__(package[0], fromlist=True)
                if hasattr(model, package[1]):
                    clazz = getattr(model, package[1])
                    if hasattr(clazz(), 'decode'):
                        func = getattr(clazz(), 'decode')
                        result = func(message.topic, message.payload)
                        if result is not None:
                            return result
            return None
        except:
            raise EnvisionException('getDecode failed')