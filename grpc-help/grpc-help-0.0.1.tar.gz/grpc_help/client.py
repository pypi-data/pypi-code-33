import socket
import grpc
from grpc_help import interceptor
from grpc_help.key import read_public_key


def client_channel(address_port, ssl=False, **kwargs):
    if ssl:
        public_key_path = kwargs.get("public_key_path")
        assert public_key_path, "certificate public_key_path can not be empty"
        trusted_certs = read_public_key(public_key_path)
        credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        channel = grpc.secure_channel(address_port, credentials)
    else:
        channel = grpc.insecure_channel(address_port)

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    headers = (("host", hostname), ("ip", ip))
    header_adder_interceptor = interceptor.header_adder_interceptor(*headers)
    return grpc.intercept_channel(channel, header_adder_interceptor)
