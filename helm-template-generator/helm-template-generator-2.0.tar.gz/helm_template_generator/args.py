import argparse


def arg_list():
    """Arg in a dict."""
    arg_list = [
        ['-p', '--project', 'the name of the project to generate template for', True],
        ['-o', '--output', 'the output path to spit templates', True],
        ['-e', '--envfile',
         'Specify the path to the json file containing the environment variables',
         True]]
    return arg_list


def arg_options():
    """Argparse options."""
    parser = argparse.ArgumentParser()
    args = arg_list()
    for arg in args:
        parser.add_argument(arg[0], arg[1],
                            help=arg[2],
                            required=arg[3])
    parsed_args = parser.parse_args(args=None, namespace=None)
    arg_dict = vars(parsed_args)
    return arg_dict


if __name__ == '__main__':
    arg_options()
