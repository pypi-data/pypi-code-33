from django.conf import settings
from django.core.management import BaseCommand

from grpc_help import grpcserver


class Command(BaseCommand):
    help = "Starts the GRPC server"

    def add_arguments(self, parser):
        parser.add_argument("addrport", nargs="?", help="Optional port number, or ipaddr:port")
        parser.add_argument(
            '-s', '--ssl', action='store_true', dest='ssl', help='Runserver with ssl')
        parser.add_argument(
            '-w', '--worker', dest="max_workers", type=int, default=4,
            help="Number of maximum worker threads")

    def handle(self, *args, **options):

        address_port = options["addrport"]
        ssl = options["ssl"]
        workers = options["workers"]
        address_port = address_port if address_port else "[::]:50051"
        ks = {}
        if ssl:
            ks["private_key_path"] = settings.GRPC_SERVER_KEY_PATH
            ks["public_key_path"] = settings.GRPC_SERVER_CERT_PATH

        grpcserver.start(address_port=address_port, ssl=ssl, workers=workers,
                         rpc_root_ruleconf=settings.GRPC_ROOT_URLCONF, **ks)
        self.stdout.write("Running GRPC server on localhost:{}".format(port))

