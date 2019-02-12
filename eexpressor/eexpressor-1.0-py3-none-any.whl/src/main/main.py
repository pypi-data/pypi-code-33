import argparse
from . import output_selector


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "emotion",
        default=None,
        help="Type in your emotion.",
        type=str)
    parser.add_argument(
        "--dict",
        default=None,
        help="Find the literal meaning of your emotion",
        action="store_true")
    parser.add_argument(
        "--img",
        default=None,
        help="Get link of random image searched with this emotion",
        action="store_true")
    parser.add_argument(
        "--translate", "-t",
        default=None,
        help="Translate this to enligsh",
        action="store_true")
    return parser


def main():
    try:
        parser = get_parser()
        arg = parser.parse_args()
        output = output_selector.get_output(arg)
        print("Output as: " + output.__str__())
        return output
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
