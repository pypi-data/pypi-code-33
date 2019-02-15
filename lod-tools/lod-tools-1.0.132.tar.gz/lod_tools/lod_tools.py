import argparse
from collections import OrderedDict
import docker
import getpass
import io
import json
import os
import re
import requests
import shutil
import sys
import zipfile

from . import basics
from . import utilities

##############################################################################################################
# constants
##############################################################################################################


PATH_PREFIX = '/lod'
INPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'in.txt')
OUTPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'out.txt')

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CONFIG.txt')
_DOCKER_EXAMPLE_NAME = 'program_example'
_DOCKER_EXAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _DOCKER_EXAMPLE_NAME)
_INPUT_EXAMPLE_NAME = 'input_example'
_INPUT_EXAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _INPUT_EXAMPLE_NAME)

def _get_server_url():
    """
    get a connection string that can be used to connect to the server
    """
    use_local_server = False
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            use_local_server = config['use_local_server']
    if use_local_server:
        url = basics.get_shared_truth()['debug_server_url']
    else:
        url = basics.get_shared_truth()['server_url']
    return url

def _get_json_encoding_of_server():
    """
    get the type of encoding that the server uses for encoding JSON strings
    """
    res = basics.get_shared_truth()['json_encoding']
    return res


##############################################################################################################
# main - initialize
##############################################################################################################


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


##############################################################################################################
# helper functions for authorization
##############################################################################################################


def require_elody_authentication(subparser):
    subparser.add_argument('-e', '--email', default=None,
        help="The password of your LOD account. This can be skipped if you have already used the 'configure' command.")
    subparser.add_argument('-p', '--password', default=None,
        help="The password of your LOD account. This can be skipped, in which case you will be asked for the password interactively.")

def check_if_elody_credentials_are_configured(args):
    """
    If the arguments contain an email, use that one.
    If not, check if there is a configuration file and use it.
    In either case, if there is no password, ask the user for a password interactively.
    """
    if args.email is None:
        if os.path.isfile(_CONFIG_FILE):
            with open(_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                args.email = config['email']
                args.password = config['password']
        else:
            raise ValueError("Email and password for LOD must be specified. Either use a configuration file for this or provide them as arguments. See --help for details.")
    # If the password isn't configured, ask for it
    if args.password is None:
        args.password = getpass.getpass()


def docker_connect(args, use_local_registry=False):
    """
    connect to the Docker registry of the LOD server.
    """
    if use_local_registry:
        client = docker.from_env()
    else:
        client = docker.from_env()
        # deprecated:
        # there used to be a login here, but it's not necessary because the docker registry on elody.com is not password protected
        #client.login(registry=basics.get_shared_truth()['docker_registry'])
    return client


##############################################################################################################
# version number check for this API
##############################################################################################################


name_of_this_library = 'lod-tools'
api_version_number_of_this_library = 2
def check_library_api_version():
    # Ask the server if this program is up to date
    data = {
        'library_name' : name_of_this_library,
        'version' : api_version_number_of_this_library,
    }
    url = _get_server_url() + 'api/check_library_api_version/'
    resp = requests.post(url, data=data)
    resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
    if 'error' in resp:
        raise Exception("error message from server:\n%s" % (resp['error'],))
    up_to_date = resp['up_to_date']
    deprecated = resp['deprecated']
    # Output a message to the user depending on whether or not the version is up to date, or deprecated
    if up_to_date:
        return
    else:
        if deprecated:
            raise Exception("This version of this library is deprecated. Upgrade to a newer version by running 'pip install --upgrade %s'." % name_of_this_library)
        else:
            print("Note: A newer version of this library is available. It can be installed by running 'pip install --upgrade %s'." % name_of_this_library)


##############################################################################################################
# main - functions
##############################################################################################################


def configure(args):
    if args.password_interactive is True:
        if args.password is not None:
            raise ValueError("Don't provide both --password and --password-interactive.")
        args.password = getpass.getpass()
    with open(_CONFIG_FILE, 'w') as f:
        config = {
            'email' : args.email,
            'password' : args.password,
            'use_local_server' : args.use_local_server,
        }
        json.dump(config, f)
    print("Successfully created configuration file.")

subparser = subparsers.add_parser('configure',
    help="""Creates a configuration file to store your login credentials, so you don't have to specify them every time.
    Be aware that anyone who steals this configuration file will be able to log in with your credentials unless you delete the file again.""")
subparser.add_argument('-e', '--email', required=True,
    help="The email of your LOD account.")
subparser.add_argument('-p', '--password', required=False,
    help="The password of your LOD account. This is not required, but if you don't specify it here you will be asked for it every time you use this tool.")
subparser.add_argument('-pi', '--password-interactive', action='store_true',
    help="Use this option instead of -p if you want to give the password interactively, but still store it in the configuration file.")
subparser.add_argument('--use-local-server', action='store_true',
    help=argparse.SUPPRESS)
subparser.set_defaults(func=configure)


def delete_configuration(args):
    if os.path.isfile(_CONFIG_FILE):
        os.remove(_CONFIG_FILE)
        return
    else:
        raise ValueError("no config file exists.")

subparser = subparsers.add_parser('delete-configuration',
    help="""Deletes the configuration file that stores your login credentials.""")
subparser.set_defaults(func=delete_configuration)


def generate_example_program(args):
    dst = args.folder
    if os.path.exists(dst):
        raise ValueError("The specified path already exists: %s" % dst)
    shutil.copytree(_DOCKER_EXAMPLE_PATH, dst)
    # manually delete the pycache that gets created for some reason...
    cache = os.path.join(dst, '__pycache__')
    if os.path.exists(cache):
        shutil.rmtree(cache)


subparser = subparsers.add_parser('generate-example-program', help="Creates an example program, as a tutorial what the files of a program for LOD should look like.")
subparser.add_argument('-f', '--folder', required=True, help="The path to the folder in which the example program will be generated.")
subparser.set_defaults(func=generate_example_program)


def generate_example_input_folder(args):
    dst = args.folder
    if os.path.exists(dst):
        raise ValueError("the specified path already exists: %s" % dst)
    shutil.copytree(_INPUT_EXAMPLE_PATH, dst)


subparser = subparsers.add_parser('generate-example-input-folder',
    help="Creates a folder with files for testing a program. To be used with test-program. Note that the generated input folder is minimalistic and just intended to make sure your Program compiles and runs properly. If you want to test things properly, you should use the folders generated while using the 'lod-executor' Program (available via pip).")
subparser.add_argument('-f', '--folder', required=True, help="The path to the folder that will be generated.")
subparser.set_defaults(func=generate_example_input_folder)


def test_docker_program(args):
    # copy files to prepare the folder in which the Docker Image will be executed
    execution_folder = os.path.abspath(args.execution_folder)
    if args.preparation_folder is not None:
        src = os.path.abspath(args.preparation_folder)
        utilities.copy_and_overwrite(src, execution_folder)
    error_file_location = os.path.join(execution_folder, "error.txt")
    log_file_location = os.path.join(execution_folder, "log.txt")
    for f in [error_file_location, log_file_location]:
        if os.path.exists(f):
            os.remove(f)
    # Determine the external domains to give access to
    required_external_domains = args.internet_access
    if required_external_domains is None:
        the_in_file = os.path.join(execution_folder, "in.txt")
        with open(the_in_file, 'r', encoding='utf8') as f:
            _input = json.load(f)
            object_manager = basics.parse_object_manager(_input['object_manager'])
            event = object_manager.get_current_event()
            program = object_manager.get_object_for_identifier(basics.parse_identifier(event.args['program_identifier']))
            required_external_domains = program.required_external_domains
    # build the Docker Image
    if not args.quiet:
        print("Compiling Docker Image...")
    client = docker_connect(None, use_local_registry=True)
    tag = "lod-program-offline-test"
    try:
        image, build_logs = client.images.build(path=os.path.abspath(args.program_folder), nocache=args.force_docker_recompilation, tag=tag)
    except Exception as e:
        print("Something went wrong while creating the Docker Image. Are you sure Docker is running and working correctly? See the below error for details:\n%s" % e)
        raise
    # If necessary, create a network to use
    # (Each Container runs on a separate network to prevent them accessing data in other Containers)
    # (This is analogous to the code in the lod-executor)
    if len(required_external_domains) == 0:
        network_for_container = None
    else:
        if 'full_internet_access' not in required_external_domains:
            raise ValueError("Docker programs can currently only get internet access to the whole internet, not to only a few websites. This feature will be added later, by adding a complex proxy. Please add 'full_internet_access' to the list of allowed domains.")
        network_name = "lod-test-program-network"
        network_for_container = client.networks.create(network_name, driver="bridge")
    # execute the Image
    if not args.quiet:
        print("Executing Docker Image as Docker Container...")
    try:
        folder_mapping = {
            os.path.abspath(args.execution_folder) : {
                'bind' : "/lod",
                'mode' : 'rw',
            },
        }
        if network_for_container is None:
            client.containers.run(image=tag, volumes=folder_mapping, remove=True, network_disabled=True)
        else:
            client.containers.run(image=tag, volumes=folder_mapping, remove=True, network=network_name)
    except docker.errors.ContainerError as error:
        print("Encountered error while executing Docker Container:")
        error_message = error.stderr.decode("utf-8")
        print(error_message)
    finally:
        # Remove the Network again
        if network_for_container is not None:
            network_for_container.remove()
    # Print either the content of the log file and the error message, if they exist
    if args.quiet:
        return
    print("Finished executing the Docker Container.")
    if args.log:
        try:
            with open(log_file_location, 'r') as log_file:
                log = log_file.read()
                if log == "":
                    print("The generated log file is empty.")
                else:
                    print("A LOG file was generated:")
                    print(log)
        except FileNotFoundError:
            pass
    try:
        with open(error_file_location, 'r') as error_file:
            error = error_file.read()
            if error == "":
                print("Warning: An error file exists, but it is empty. This should not be possible.")
            else:
                print("An ERROR file was generated:")
                print(error)
    except FileNotFoundError:
        pass


subparser = subparsers.add_parser('test-program',
    help="Creates a Docker Image locally, based on a program folder. Executes that Image the same way it will be executed on the server.")
subparser.add_argument('-p', '--program-folder', required=True, help="The path to the folder containing the Dockerfile of the Program to generate.")
subparser.add_argument('-e', '--execution-folder', required=True, help="The path to the folder in which the Docker Image will be executed.")
subparser.add_argument('-prep', '--preparation-folder', default=None,
    help="The path to a folder containing files that will be copied into the execution-folder before the execution, overwriting it. Note that all other files in the execution-folder will be deleted.")
subparser.add_argument('-rec', '--force-docker-recompilation', action='store_true',
    help="Ignore the Docker cache and always recompile. This may be useful for debugging if you are e.g. modifying external dependencies, since Docker will skip recompilation if the only thing that changed were external files.")
subparser.add_argument('-i', '--internet-access', nargs='+', default=None,
    help="Gives the Program access to external domains by creating a temporary Docker Network for it. If this option is not specified, the Program has access to the same domains as it did in its original execution, based on the file in.txt in the --execution-folder.")
subparser.add_argument('-q', '--quiet', action='store_true',
    help="Don't print anything to the console.")
subparser.add_argument('-l', '--log', action='store_true',
    help="Print the content of the log file after running the program.")
subparser.set_defaults(func=test_docker_program)


def upload_program(args):
    if args.quiet and args.verbose:
        raise ValueError("Can't be both quiet and verbose at the same time")
    check_if_elody_credentials_are_configured(args)
    check_library_api_version()
    folder = args.folder
    if args.name is None:
        program_name = os.path.basename(folder)
    else:
        program_name = args.name
    use_local_server = False
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            use_local_server = config['use_local_server']
    program_description = args.description
    required_external_domains = args.required_external_domains
    full_image_name_with_registry = "%s/%s" % (basics.get_shared_truth()['docker_registry'], program_name.lower(),)
    #
    # Get the description
    #
    descr_file_path = os.path.join(folder, 'DESCRIPTION.txt')
    if program_description is None:
        if os.path.isfile(descr_file_path):
            with open(descr_file_path, 'r') as f:
                program_description = f.read()
        else:
            program_description = "No description given."
    #
    # Get the required_external_domains
    #
    domains_file_path = os.path.join(folder, 'DOMAINS.txt')
    if required_external_domains is None:
        if os.path.isfile(domains_file_path):
            with open(domains_file_path, 'r') as f:
                required_external_domains = f.read()
        else:
            required_external_domains = ""
    else:
        required_external_domains = ' '.join(required_external_domains)
    #
    # Get miscellaneous arguments
    #
    max_execution_duration = args.max_execution_duration
    if max_execution_duration is None:
        max_execution_duration = basics.get_shared_truth()['new_program_default_max_execution_duration']
    #
    # Build the Docker image
    #
    # find out how many versions of the Image already exist, if any
    if not args.quiet:
        print("Compiling Docker Image...")
    client = docker_connect(args, use_local_registry=use_local_server)
    try:
        image, build_logs = client.images.build(path=folder, nocache=args.force_docker_recompilation)
    except Exception as e:
        print("Something went wrong while creating the Docker Image. Are you sure Docker is running and working correctly? See the below error for details:\n%s" % e)
        raise
    #
    # If required, upload the source code as well
    #
    no_source_upload = args.no_source_upload
    files = {}
    if not no_source_upload:
        virtual_file = io.BytesIO()
        zip_handle = zipfile.ZipFile(virtual_file, 'w', zipfile.ZIP_DEFLATED)
        utilities.zipdir(folder, zip_handle)
        zip_handle.close()
        files['source_files_archive'] = virtual_file.getvalue()
    #
    # Notify the LOD server
    # (and optionally upload the files)
    #
    if not args.quiet:
        print("Contacting LOD server...")
    data = {
        'email' : args.email,
        'password' : args.password,
        'program_name' : program_name,
        'is_release_version' : args.release,
        'program_description' : program_description,
        'required_external_domains' : required_external_domains,
        'max_execution_duration' : max_execution_duration,
    }
    url = _get_server_url() + 'api/upload_program_1/'
    resp = requests.post(url, data=data, files=files)
    resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
    #
    # Print the response received from the server
    #
    if 'error' in resp:
        raise Exception("Error message from server:\n%s" % (resp['error'],))
    program_id = resp['id']
    program_name = resp['name']
    version = resp['version']
    response_text = resp['response_text']
    if args.verbose:
        print(response_text)
    #
    # Tag the Image with the right version number and push it to the registry server
    #
    # Tag the image
    tag = "version-%d" % (version,)
    full_identifier = '%s:%s' % (full_image_name_with_registry, tag)
    if not args.quiet:
        print("Tagging and uploading Docker Image: %s" % (full_identifier,))
    # (tagging with this API apparently works by just building the Image again and relying on the cache to avoid actually rebuilding it)
    image, build_logs = client.images.build(path=folder, tag=full_identifier)
    image_digest = None
    # Push to the registry
    # (unless we are running in the developer-only local mode for faster testing of the website)
    if not use_local_server:
        for line in client.images.push(full_image_name_with_registry, tag=tag, stream=True):
            msgs = [json.loads(a) for a in line.decode('utf-8').split('\n') if a != ""]
            for msg in msgs:
                if 'error' in msg:
                    raise Exception(msg['error'])
                elif 'status' in msg:
                    if args.verbose:
                        print("\t%s" % (msg['status'],))
                    # Get the image's digest
                    match = re.search(r'digest: (sha256:[0-9a-zA-Z]+)', msg['status'])
                    if match:
                        image_digest = match.group(1)
    if image_digest is None:
        if use_local_server:
            docker_upload_successful = True
            image_identification = full_identifier
        else:
            docker_upload_successful = False
            image_identification = None
    else:
        docker_upload_successful = True
        image_identification = '%s@%s' % (full_image_name_with_registry, image_digest)
    #
    # Notify the LOD server a second time after the Docker Image has been uploaded
    #
    if docker_upload_successful:
        if not args.quiet:
            print("Activating Image on server...")
        data = {
            'email' : args.email,
            'password' : args.password,
            'program_id' : program_id,
            'image_identification' : image_identification,
        }
        url = _get_server_url() + 'api/upload_program_2/'
        resp = requests.post(url, data=data)
        resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
        #
        # Print the response received from the server
        #
        if 'error' in resp:
            raise Exception("Error message from server:\n%s" % (resp['error'],))
        response_text = resp['response_text']
        if args.verbose:
            print(response_text)
    #
    # Done.
    #
    if not args.quiet:
        print("Done. Created version %d of Program '%s' with id=%d, with Docker Image:\n%s" % (version, program_name, program_id, full_identifier,))

subparser = subparsers.add_parser('upload-program',
    help="""upload a program to the server, making it available for use by execution rules.
    Can be used for creating new programs, or updating existing ones.""")
subparser.add_argument('-f', '--folder', required=True,
    help="the path to the folder that should be uploaded. This should target the directory in which the Dockerfile is located.")
subparser.add_argument('-r', '--release', action='store_true',
    help="if this flag is set, the program is uploaded as a release version. Otherwise it is uploaded as a development version.")
subparser.add_argument('-n', '--name', default=None,
    help="the name of the program. Defaults to the name of the folder in which the program is stored. If a Program with this name already exists, a new version of it will be created. Otherwise, a new program is created.")
subparser.add_argument('-d', '--description', default=None,
    help="a short description of the program. If none is given, defaults to the content of the file 'DESCRIPTION.txt' stored in the folder that is being uploaded, if one exists.")
subparser.add_argument('-red', '--required-external-domains', nargs='+', default=None,
    help="""A list of internet domains the Program needs access to. If none are given, defaults to the content of the file 'DOMAINS.txt' stored in the folder that is being uploaded (the domains should be separated with whitespace). If no such file exists, the Program is marked as requiring no external domains. Domains are listed in the same format as the 'external_domains' here: https://elody.com/tutorial/documentation_rules/#message_component_html.
    NOTE: For technical reasons, programs currently can't be limited to only some domains (we are working on it!). For now, if you list any domains, it will automatically ask the user to allow full internet access instead of asking only for the domains you specified.""")
subparser.add_argument('--max-execution-duration', type=float, default=None,
    help="the time, in seconds, that the program will be executed for before being quit by force, unless this is specified otherwise by whatever caused the program's execution. Defaults to %f" % (basics.get_shared_truth()['new_program_default_max_execution_duration'],))
subparser.add_argument('--no-source-upload', action='store_true',
    help="do not upload the source files to the LOD server, to make them available for inspection.")
subparser.add_argument('-rec', '--force-docker-recompilation', action='store_true',
    help="ignore the Docker cache and always recompile. This may be useful for debugging if you are e.g. modifying external dependencies, since Docker will skip recompilation if the only thing that changed were external files.")
subparser.add_argument('-q', '--quiet', action='store_true',
    help="don't print anything to the console.")
subparser.add_argument('-v', '--verbose', action='store_true',
    help="print lots of extra information to the console.")
require_elody_authentication(subparser)
subparser.set_defaults(func=upload_program)


def download_program(args):
    check_if_elody_credentials_are_configured(args)
    check_library_api_version()
    folder = args.folder
    if folder is None:
        folder = os.getcwd()
    id = args.identifier
    name = args.name
    version = args.version
    if id is None and name is None:
        raise ValueError("either the name or the ID of the program must be given.")
    if id is not None and name is not None:
        raise ValueError("only one out of the name and the ID of the program must be given, not both.")
    if name is not None and '#' in name:
        if version is not None:
            raise ValueError("don't specify the version both directly and indirectly (as part of the name). One of the two suffices.")
        tmp = name.split('#')
        name = tmp[0]
        version = tmp[1]
        if len(tmp) != 2:
            raise ValueError("invalid name format. Use either '<program_name>'' or '<program_nam>#<version>'.")
    if id is not None and version is not None:
        raise ValueError("don't specify a version along with an ID. IDs identify programs unambiguously. Only names are ambiguous and need clarification.")
    #
    # notify the LOD server
    #
    data = {}
    if name is not None:
        data['name'] = name
    if version is not None:
        data['version'] = int(version)
    if id is not None:
        data['id'] = int(id)
    url = _get_server_url() + 'api/download_program/'
    resp = requests.post(url, data=data)
    #
    # print the response received from the server
    #
    response_file = resp._content
    response_data = json.loads(resp.headers['additional_response_data'])
    if 'error' in response_data:
        raise Exception("error message from server:\n%s" % (response_data['error'],))
    response_text = response_data['response_text']
    id = response_data['id']
    name = response_data['name']
    version = response_data['version']
    source_code_exists = response_data['source_code_exists']
    if not args.quiet:
        print(response_text)
    #
    # unzip the file, if there is one
    #
    if not args.quiet:
        print("retrieved program: id=%d, name='%s', version=%d" % (id, name, version,))
    if source_code_exists:
        if not args.quiet:
            print("unpacking files...")
        unzipped_path = os.path.join(folder, "%s-version-%d" % (name, version,))
        zip_ref = zipfile.ZipFile(io.BytesIO(response_file), 'r')
        zip_ref.extractall(unzipped_path)
        zip_ref.close()
        if not args.quiet:
            print("done.")
    else:
        if not args.quiet:
            print("no source code for this Program and version was made available.")

subparser = subparsers.add_parser('download-program',
    help="""download a program from the server.""")
subparser.add_argument('-f', '--folder', default=None,
    help="the path to the folder where the downloaded program should be placed. The folder containing the program will be put inside this folder. Defaults to the current directory.")
subparser.add_argument('-id', '--identifier', default=None,
    help="the ID of the program to download.")
subparser.add_argument('-n', '--name', default=None,
    help="""the name of the program to download. If no version is provided along with this, you get the latest version.
    The version can either be specified explicitly, through the --version tag, or by appending '#<version>' to the name.""")
subparser.add_argument('-v', '--version', default=None,
    help="the version of the program to download. This is only meaningful when combined with the program's name.")
subparser.add_argument('-q', '--quiet', action='store_true',
    help="don't print anything to the console.")
require_elody_authentication(subparser)
subparser.set_defaults(func=download_program)


def create_symbols(args):
    check_if_elody_credentials_are_configured(args)
    check_library_api_version()
    # load the file
    with open(args.file, 'r') as f:
        symbols_list = utilities.parse_loosely_defined_json(f.read())
    # send a request to the server
    data = {
        'email' : args.email,
        'password' : args.password,
        'symbols_as_list' : json.dumps(symbols_list),
    }
    url = _get_server_url() + 'api/create_symbols/'
    resp = requests.post(url, data=data)
    resp = resp._content.decode(_get_json_encoding_of_server())
    resp = json.loads(resp)
    #
    # print the response received from the server
    #
    if 'error' in resp:
        raise Exception("error message from server:\n%s" % (resp['error'],))
    response_text = resp['response_text']
    print(response_text)
    cleaned_symbols_list = json.loads(resp['symbols_as_list'])
    if args.result is not None:
        # before printing the symbols to file, go through them and change the way they are displayed
        sort_order = ['name', 'placeholder', 'description']
        cleaned_symbols_list = [OrderedDict(sorted(a.items(), key=lambda kv: sort_order.index(kv[0]))) for a in cleaned_symbols_list]
        with open(args.result, 'w') as f:
            json.dump(cleaned_symbols_list, f, indent=4)
        print("created file for the defined Symbols: '%s'" % args.result)


subparser = subparsers.add_parser('create-symbols', help="creates all the Symbols specified in the file. See the tutorial of the lod-tools for details on how this works.")
subparser.add_argument('-f', '--file', required=True, help="the path to the file that contains the definition of the Symbols")
subparser.add_argument('-r', '--result', help="the path to the file that is generated if the Symbols are created successfully and contains their full details.")
require_elody_authentication(subparser)
subparser.set_defaults(func=create_symbols)


def upload_rule(args):
    check_if_elody_credentials_are_configured(args)
    check_library_api_version()
    # load the file
    # parse it using parse_loosely_defined_json(), so it doesn't complain about minor issues like extra commas
    with open(args.file, 'r') as f:
        rule_dictionary = utilities.parse_loosely_defined_json(f.read())
    # optionally load the symbol file and extract placeholders and apply them
    if args.symbols is not None:
        symbol_placeholders = {}
        with open(args.symbols, 'r') as f:
            symbols_list = utilities.parse_loosely_defined_json(f.read())
            for s in symbols_list:
                if 'placeholder' in s:
                    placeholder = '$' + s['placeholder']
                    symbol_placeholders[placeholder] = s['name']
        # verify the format of the symbol_placeholders
        # then overwrite all occurrences of the symbol_placeholders within the file
        error_message = "the 'symbol_placeholders' must be a dictionary mapping strings to strings"
        if not isinstance(symbol_placeholders, dict):
            raise ValueError(error_message)
        for k,v in symbol_placeholders.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError(error_message)
        # apply the placeholders to the rule_dictionary
        def _recursive_placeholder_substitutor(obj):
            if isinstance(obj, dict):
                return { k:_recursive_placeholder_substitutor(v) for k,v in obj.items()}
            elif isinstance(obj, list):
                return [_recursive_placeholder_substitutor(a) for a in obj]
            elif isinstance(obj, str) and obj in symbol_placeholders:
                return symbol_placeholders[obj]
            return obj
        rule_dictionary = _recursive_placeholder_substitutor(rule_dictionary)
    # determine the name of the rule from the filename
    # or from the content of the file
    rule_name = os.path.splitext(os.path.basename(args.file))[0]
    if not isinstance(rule_dictionary, dict):
        raise Exception("the rule must be defined as a dictionary of values / a JSON Object")
    if 'name' in rule_dictionary:
        rule_name = rule_dictionary['name']
    else:
        rule_dictionary['name'] = rule_name
    # send a request to the server
    print("uploading rule '%s'" % (rule_name,))
    data = {
        'email' : args.email,
        'password' : args.password,
        'rule_as_dictionary' : json.dumps(rule_dictionary),
        'debugging_only' : json.dumps(True if args.debugging_only else False),
        'deactivate_older_versions' : json.dumps(True if args.deactivate else False),
    }
    url = _get_server_url() + 'api/upload_rule/'
    resp = requests.post(url, data=data)
    resp = resp._content.decode(_get_json_encoding_of_server())
    resp = json.loads(resp)
    #
    # print the response received from the server
    #
    if 'error' in resp:
        raise Exception("error message from server:\n%s" % (resp['error'],))
    response_text = resp['response_text']
    print(response_text)
    cleaned_rule_dict = json.loads(resp['rule_as_dictionary'])
    if args.result is not None:
        with open(args.result, 'w') as f:
            json.dump(cleaned_rule_dict, f, indent=4)
        print("created file for the final rule: '%s'" % args.result)


subparser = subparsers.add_parser('upload-rule', help="""uploads a file describing a rule. If successful, this creates a new Rule on the server.""")
subparser.add_argument('-t', '--debugging-only', action='store_true',
    help="if this is set, the rule will not be created, but error messages will still be shown. Useful to debug if you get error messages while uploading and/or want to experiment. Works well with --result, since you can inspect what your code gets turned into.")
subparser.add_argument('-f', '--file', required=True, help="the path to the file to be uploaded.")
subparser.add_argument('-s', '--symbols', help="the path to a file of Symbols that has been generated as the output of a create-symbols command. The Symbols in that file can be referenced by the Rule through their placeholder value by writing '$<placeholder_name>' instead of '<symbol_name>'. This is an optional feature used for convenience.")
subparser.add_argument('-d', '--deactivate', action='store_true',
    help="whether or not to deactivate all existing rules with the same name.")
subparser.add_argument('-r', '--result',
    help="""if this parameter is given, the fully parsed and created rule is written to the selected file.
    This may differ in some ways from the original file, for instance because default values are set.""")
require_elody_authentication(subparser)
subparser.set_defaults(func=upload_rule)


def delete_rule(args):
    check_if_elody_credentials_are_configured(args)
    check_library_api_version()
    # send a request to the server
    data = {
        'email' : args.email,
        'password' : args.password,
        'rule_id' : args.id,
        'rule_name' : args.name,
        'rule_version' : args.version,
    }
    url = _get_server_url() + 'api/delete_rule/'
    resp = requests.post(url, data=data)
    resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
    #
    # print the response received from the server
    #
    if 'error' in resp:
        raise Exception("error message from server:\n%s" % (resp['error'],))
    response_text = resp['response_text']
    print(response_text)


subparser = subparsers.add_parser('delete-rule', help="deletes one or more existing rules you own.")
subparser.add_argument('-i', '--id', required=False, help="the ID of the rule.")
subparser.add_argument('-n', '--name', required=False, help="the name of the rule.")
subparser.add_argument('-v', '--version', required=False, help="the version of the rule.")
require_elody_authentication(subparser)
subparser.set_defaults(func=delete_rule)


##############################################################################################################
# main - finalize
##############################################################################################################


def main():
    if len(sys.argv)==1:
        # if the program is called without arguments, print the help menu and exit
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()
        args.func(args)

if __name__ == '__main__':
    main()
