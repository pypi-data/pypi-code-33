from image_file_name_fixer import name_fixer
from .argument_processor import ArgumentProcessor


def main():
    """The main routine."""

    arg_processor = ArgumentProcessor()
    app_config = arg_processor.process_args()
    name_fixer.run(app_config)


if __name__ == '__main__':
    main()
