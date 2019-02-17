"""
This module handles the application's configuration.
"""


class AppConfig:
    """
    This class encapsulates the application's configuration.

    :member dry_run: The application should run in dry run mode.  No destructive changes should be done.  Boolean value.
    :member should_move_file: The application should move the file, rather than copy it.  Boolean value.
    :member verbose: The application should run in verbose mode.  Output should include image_detail dump.
                     Boolean value.
    :member paths: Input file paths.  List of strings.  List value.
    :member output_dir: The application should copy/move output files to this directory.  If it does not exist, use the
                        current working directory.  String value.
    """
    def __init__(self, args):
        """
         AppConfig constructor.  Initialize this object with parsed command line arguments.

         :param args: Parsed command line arguments.
         :returns nothing:
         """
        self.version = args.version
        self.dry_run = args.dry_run
        self.recursive = args.recursive
        self.should_move_file = args.should_move_file
        self.verbose = args.verbose
        self.paths = args.paths
        # Only used if output_dir is given as a command line argument.
        self.output_dir = args.output_dir

    def get_paths(self):
        """ :returns path: """
        return self.paths

    def get_output_dir(self):
        """ :returns output_dir: """
        return self.output_dir
