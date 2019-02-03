import argparse
import sys

from GBARPGMaker.GBARPGMaker import GBARPGMaker

def main():
    parser = argparse.ArgumentParser(description='GBARPGMaker description')

    parser.add_argument("command", choices=["new", "make", "inter"])

    args = parser.parse_args()

    if args.command == "new":
        pass
    elif args.command == "make":
        sys.path.append("./")

        import config

        grm = GBARPGMaker(config)
        grm.make_game()
    elif args.command == "inter":
        sys.path.append("./")

        import config

        grm = GBARPGMaker(config)
        m = grm.maps[list(grm.maps.keys())[0]]
        s = grm.sprite_images[list(grm.sprite_images.keys())[0]]
        __import__('IPython').embed()


if __name__ == "__main__":
    main()
