import cone
import sys

from console_cone import get_parser


def main():
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    try:
        if args.command == "help":
            parser.print_help()

        elif args.command == "version":
            print("Running cone version {}".format(cone.version()))

        elif args.command == "revert":
            cone_server = cone.Server(port=args.port)
            cone_exit = cone.revert(cone_server)
            cone_exit.print()

        elif args.command == "test":
            cone_server = cone.Server(port=args.port)
            cone_exit = cone.test(cone_server)
            cone_exit.print()

        elif args.command == "deploy":
            cone_server = cone.Server(port=args.port)
            cone_exit = cone.deploy(cone_server, args.include_tests, args.obfuscate)
            cone_exit.print()

    except cone.ConeExit as cone_exit:
        cone_exit.print()


if __name__ == "__main__":
    main()
