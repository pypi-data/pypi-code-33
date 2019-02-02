import socket
import time

from pyready.base import wait_for_connection, get_argparser, TestConnectionResult


def test_tcp_connection(host: str, port: int, n_retries: int, wait_time: float, verbose: bool=True):
    def test_func():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            s.close()
        except socket.error as ex:
            if ex.strerror == 'Connection refused':
                time.sleep(wait_time)
                return TestConnectionResult.timeout()

            return TestConnectionResult.error("Connection failed with errno {0}: {1}".format(ex.errno, ex.strerror))

        return TestConnectionResult.success()

    return wait_for_connection(test_func, f"Test TCP Connection at {host}:{port}", n_retries, verbose)


if __name__ == '__main__':
    parser = get_argparser(description="")
    parser.add_argument("-r", "--retries", type=int, default=10, help="number of retries (default 10)")
    parser.add_argument("-w", "--wait_time", type=float, default=0.5, help="default wait time between different tries")
    parser.add_argument("-v", "--verbose", type="boolean", default=True, help="enable/disable printing messages (default true)")
    parser.add_argument("host", type=str, help="host name or ip address")
    parser.add_argument("port", type=int, help="port number")

    args = parser.parse_args()
    resp = test_tcp_connection(args.host, args.port, args.retries, args.verbose)
    exit(0 if resp else 1)
