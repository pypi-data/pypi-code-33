import psycopg2, time

from pyready.base import TestConnectionResult, wait_for_connection, get_argparser
from pyready.telnet import test_tcp_connection


def test_postgres_connection(db_host: str, db_port: int, db_name: str, user: str, pwd: str, n_retries: int, wait_time: float, verbose: bool=True):
    def test_func():
        try:
            conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=user, password=pwd, connect_timeout=2)
            conn.close()
        except psycopg2.OperationalError as ex:
            str_ex = str(ex)
            if any(str_ex.find(x) != -1 for x in ['timeout expired', 'the database system is starting up']):
                time.sleep(wait_time)
                return TestConnectionResult.timeout()
            return TestConnectionResult.error("Connection failed with error: {0}".format(ex))

        return TestConnectionResult.success()

    if not test_tcp_connection(db_host, db_port, n_retries, wait_time, verbose):
        return False


    if wait_for_connection(test_func, f"Test Postgres Connection at {db_host}:{db_port}/{db_name}", n_retries, verbose):
        # after started for the first time, postgres db may restart and cause interruption
        # so we give it sometime if it reboots
        time.sleep(wait_time)
        return wait_for_connection(test_func, f"Test Postgres Connection at {db_host}:{db_port}/{db_name}", n_retries, verbose)
    return False


if __name__ == '__main__':
    parser = get_argparser(description="")
    parser.add_argument("-r", "--retries", type=int, default=10, help="number of retries (default 10)")
    parser.add_argument("-w", "--wait_time", type=float, default=0.5, help="default wait time between different tries")
    parser.add_argument("-v", "--verbose", type="boolean", default=True,
                        help="enable/disable printing messages (default true)")

    parser.add_argument("-u", "--user", type=str, help="user name")
    parser.add_argument("-p", "--password", type=str, help="password")
    parser.add_argument("host", type=str, help="host name or ip address")
    parser.add_argument("port", type=int, help="port number")
    parser.add_argument("db_name", type=str, help="Database name")

    args = parser.parse_args()
    resp = test_postgres_connection(args.host, args.port, args.db_name, args.user, args.password, args.retries, args.verbose)
    exit(0 if resp else 1)
