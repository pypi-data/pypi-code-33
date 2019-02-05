import socket
def get_net_state_info():
    try:
        # return "OK"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        result =(s.getsockname()[0])
        s.close()
        return result
        pass
    except Exception as e:
        return str(e)
        pass