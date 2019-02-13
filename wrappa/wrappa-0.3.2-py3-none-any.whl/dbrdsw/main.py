import argparse

# from .app import App
# from .common import read_config

from dbrdsw import App, read_config


def main():
    parser = argparse.ArgumentParser(description='Process config.yml file')
    parser.add_argument('--config', '-c', default='./config.yml',
                        help='path to config.yml (default: ./config.yml)')

    args = parser.parse_args()

    config = read_config(args.config)
    app = App(**config)
    app.start()


if __name__ == '__main__':
    main()
