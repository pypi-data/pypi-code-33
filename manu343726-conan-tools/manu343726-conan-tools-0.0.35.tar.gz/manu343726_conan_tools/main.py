import argparse, importlib, logging, sys

MODULES=['ci_generator', 'python_package_recipe_generator']

def main():
    parser = argparse.ArgumentParser('manu343726-conan-tools', description='Miscellaneous tools for conan.io recipe development')
    parser.add_argument('-d', '--debug', help='Enable debug logging', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    for module_name in MODULES:
        module = importlib.import_module('manu343726_conan_tools.' + module_name)
        module.setup_argparser(subparsers)

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    args.func(args)

if __name__ == "__main__":
    main()
