import sys
import ntpath
import json
import traceback
import re
import os
from asm_api import Handler
from clparser import CreateParser
from os import path, listdir
sys.path.append(ntpath.dirname(ntpath.abspath(__file__)))
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    pass

PARSER = CreateParser().create_parser()
VALUESPACE = PARSER.parse_args(sys.argv[1:])

if len(sys.argv[1:])==0:
    PARSER.print_help()
    PARSER.exit()

main_args = ['host', 'port', 'token', 'timeout', 'command']
args = vars(PARSER.parse_args())
for arg in main_args:
    del args[arg]
# if not any(args.values()):
#     PARSER.error('No arguments provided.')


if not VALUESPACE.token or VALUESPACE.token == "0":
    try:
        CONFIG_FILE = ConfigParser.ConfigParser()
        for filename in os.listdir('..'):
            if re.match("asm_api*", filename):
                settings_path = filename
        CONFIG_FILE.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "{}/settings.ini".format(settings_path)))
        VALUESPACE.token = CONFIG_FILE.get(VALUESPACE.host, 'TOKEN')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as exception:
        print("{}. Token (--token) must be specified.".format(exception))
        sys.exit(1)


ASM = Handler(host=VALUESPACE.host,
              port=VALUESPACE.port,
              token=VALUESPACE.token,
              timeout=VALUESPACE.timeout)


def json_print(value):
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def is_alias(component):
    aliases = ASM.get_all_aliases()
    if component in aliases:
        return aliases[component]
    return None


if __name__ == '__main__':
    if VALUESPACE.command == "upload":
        if VALUESPACE.file:
            for package in VALUESPACE.file:
                if package.endswith(('zip', 'tar.gz')):
                    ASM.upload(package)
                else:
                    onlyfiles = [f for f in listdir(package) if path.isfile(path.join(package, f))]
                    for f in onlyfiles: 
                        ASM.upload(path.join(package, f))
        else:
            print("At least 1 file (-f/--file) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "download":
        for url in VALUESPACE.url:
            if VALUESPACE.auth:
                url = "{}://{}@{}".format(url.split("://")[0], VALUESPACE.auth, url.split("://")[1])
            RESULT = ASM.download(url)
            if RESULT != ASM.status_ok:
                print(RESULT)

    elif VALUESPACE.command == "install":
        if VALUESPACE.package:
            for package in VALUESPACE.package:
                RESULT = ASM.install(package)
                if RESULT != ASM.status_fail:
                    print(RESULT)
                else:
                    print('An error occurred while installing "{}".'.format(package))
        else:
            print("At least 1 package (-p/--package) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "set":
        if VALUESPACE.component:
            if VALUESPACE.key:
                if VALUESPACE.value:
                    for component in VALUESPACE.component:
                        component_id = is_alias(component)
                        if component_id:
                            component = component_id
                        if VALUESPACE.key.lower().endswith(ASM.text_extensions):
                            RESULT = ASM.set_xml(component, VALUESPACE.key, VALUESPACE.value)
                        else:
                            RESULT = ASM.set_json(VALUESPACE.key, VALUESPACE.value, component)
                        if RESULT != ASM.status_ok:
                            print(RESULT)
                else:
                    print("Value (-v/--value) must be specified.")
                    sys.exit(1)
            else:
                print("Key (-k/--key) must be specified.")
                sys.exit(1)
        else:
            print("At least 1 component (-c/--component) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "get":
        if VALUESPACE.component:
            if not VALUESPACE.property:
                VALUESPACE.property = ["all"]
            for component in VALUESPACE.component:
                if component.lower() == 'files':
                    for prop in VALUESPACE.property:
                        RESULT = ASM.get_files(prop)
                        if RESULT != ASM.status_fail:
                            for package in RESULT:
                                print(package)
                        else:
                            print(RESULT)

                elif component.lower() == 'users':
                    for user in VALUESPACE.property:
                        RESULT = ASM.get_users(user)
                        if isinstance(RESULT, list):
                            for asm_user in RESULT:
                                print()
                                json_print(asm_user)
                        else:
                            json_print(RESULT)

                elif component.lower() == 'conf':
                    for prop in VALUESPACE.property:
                        RESULT = ASM.get_conf(prop)
                        if prop == 'all':
                            json_print(RESULT)
                        else:
                            print(RESULT)

                elif component.lower() == 'task':
                    for prop in VALUESPACE.property:
                        component_id = is_alias(prop)
                        if component_id:
                            prop = component_id
                        RESULT = ASM.get_task(prop)
                        if RESULT != ASM.status_fail:
                            if isinstance(RESULT, dict):
                                json_print(RESULT)
                            elif isinstance(RESULT, list):
                                for task in RESULT:
                                    print(task)
                            else:
                                print(RESULT)
                        else:
                            print(RESULT)

                elif component.lower() == "export":
                    RESULT = ASM.get_export()
                    if RESULT != ASM.status_fail:
                        json_print(RESULT)

                else:
                    component_id = is_alias(component)
                    if component_id:
                        component = component_id
                    for prop in VALUESPACE.property:
                        if prop.lower().endswith(ASM.text_extensions):
                            RESULT = ASM.get_xml(component, prop)
                        else:
                            RESULT = ASM.get_component(component, prop)
                        if RESULT:
                            if isinstance(RESULT, dict):
                                json_print(RESULT)
                            else:
                                print(RESULT)
        else:
            print("At least 1 component (-c/--component) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "delete":
        if VALUESPACE.component:
            for component in VALUESPACE.component:
                if component.endswith(('zip', 'tar.gz')):
                    RESULT = ASM.delete_files(component)
                    if RESULT != ASM.status_ok:
                        print(RESULT)
                else:
                    component_id = is_alias(component)
                    if component_id:
                        component = component_id
                    RESULT = ASM.delete_task(component)
                    if RESULT != ASM.status_ok:
                        print(RESULT)
        else:
            print("At least 1 component (-c/--component) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "start" \
            or VALUESPACE.command == "stop"\
            or VALUESPACE.command == "restart"\
            or VALUESPACE.command == "script":
        if VALUESPACE.component:
            if "all" in VALUESPACE.component:
                RESULT = ASM.action("all", VALUESPACE.command)
                if RESULT != ASM.status_ok:
                    print(RESULT)
            else:
                for component in VALUESPACE.component:
                    component_id = is_alias(component)
                    if component_id:
                        component = component_id
                    if len(component.split("_")) == 2:
                        RESULT = ASM.action(component, VALUESPACE.command)
                        if RESULT != ASM.status_ok:
                            print(RESULT)
                    else:
                        COMPONENTS_LIST = ASM.get_task(component)
                        for COMPONENT in COMPONENTS_LIST:
                            RESULT = ASM.action(COMPONENT, VALUESPACE.command)
                            if RESULT != ASM.status_ok:
                                print(RESULT)
        else:
            print("At least 1 component (-c/--component) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "kill":
        RESULT = ASM.kill(VALUESPACE.pid)
        if RESULT != ASM.status_ok:
            print(RESULT)

    elif VALUESPACE.command == "log":
        if VALUESPACE.component:
            if VALUESPACE.path:
                for component in VALUESPACE.component:
                    component_id = is_alias(component)
                    if component_id:
                        component = component_id
                    RESULT = ASM.get_log(component, VALUESPACE.path)
            else:
                print("Path (-p/--path) must be specified.")
                sys.exit(1)
        else:
            print("At least 1 component (-c/--component) must be specified.")
            sys.exit(1)

    elif VALUESPACE.command == "info":
        for prop in VALUESPACE.property:
            RESULT = ASM.get_info(prop)
            if isinstance(RESULT, dict):
                json_print(RESULT)
            else:
                print(RESULT)

    elif VALUESPACE.command == "process":
        if VALUESPACE.key:
            if not VALUESPACE.value:
                PARSER.error("Value -v/--value not specified.")
        if VALUESPACE.value:
            if not VALUESPACE.key:
                PARSER.error("Key -k/--key not specified.")

        RESULT = ASM.get_process(VALUESPACE.property, VALUESPACE.key, VALUESPACE.value)
        if isinstance(RESULT, dict):
            json_print(RESULT)
        elif isinstance(RESULT, list):
            for item in RESULT:
                print(item)
        else:
            print(RESULT)


    elif VALUESPACE.command == "rules":
        if VALUESPACE.get:
            print(ASM.get_rules())
        elif VALUESPACE.set != None:
            RESULT = ASM.set_rules(VALUESPACE.set)
            if RESULT != ASM.status_ok:
                print(RESULT)
        elif VALUESPACE.enable:
            ASM.set_conf("enable_rules", True)
        elif VALUESPACE.disable:
            ASM.set_conf("enable_rules", False)
        else:
            PARSER.error('No arguments provided.')

    elif VALUESPACE.command == "conf":
        ASM.set_conf(VALUESPACE.key, VALUESPACE.value)

    elif VALUESPACE.command == "alias":
        COMPONENT = VALUESPACE.component
        ALIAS = VALUESPACE.alias

        COMPONENT_ID = is_alias(COMPONENT)
        if COMPONENT_ID:
            COMPONENT = COMPONENT_ID
        RESULT = ASM.set_alias(COMPONENT, ALIAS)
        if RESULT != ASM.status_ok:
            print(RESULT)

    elif VALUESPACE.command == "task":
        if not VALUESPACE.component:
            if not bool(VALUESPACE.key and VALUESPACE.value and not VALUESPACE.component):
                if not bool(VALUESPACE.component and (VALUESPACE.value or VALUESPACE.key)):
                    VALUESPACE.component = ["all"]
                else:
                    if not VALUESPACE.component:
                        PARSER.error("Component -c/--component not specified.")
                    if VALUESPACE.value and not VALUESPACE.key:
                        PARSER.error("Key -k/--key not specified.")
            else:
                PARSER.error("Component -c/--component not specified.")
        for component in VALUESPACE.component:
            COMPONENT_ID = is_alias(component)
            if COMPONENT_ID:
                component = COMPONENT_ID
            if not bool(VALUESPACE.value or VALUESPACE.key):
                RESULT = ASM.get_task(component)
                if RESULT != ASM.status_fail:
                    if isinstance(RESULT, dict):
                        json_print(RESULT)
                    elif isinstance(RESULT, list):
                        for task in RESULT:
                            print(task)
                    else:
                        print(RESULT)
                else:
                    print(RESULT)
            elif not VALUESPACE.value:
                RESULT = ASM.get_task(component)
                if RESULT:
                    if isinstance(RESULT, list):
                        for res in RESULT:
                            print(ASM.get_task(res)[VALUESPACE.key])
                    else:
                        try:
                            print(RESULT[VALUESPACE.key])
                        except KeyError as exception:
                            traceback.print_exc()
            else:
                if VALUESPACE.key:
                    RESULT = ASM.set_task(component, VALUESPACE.key, VALUESPACE.value)
                    if RESULT != ASM.status_ok:
                        print(RESULT)
                else:
                    PARSER.error("Key -k/--key not specified.")

    elif VALUESPACE.command == "lib":
        if VALUESPACE.upload != None:
            for lib in VALUESPACE.upload:
                if lib.endswith(('zip', 'tar.gz')):
                    ASM.lib_upload(lib)
                else:
                    onlyfiles = [f for f in listdir(lib) if path.isfile(path.join(lib, f))]
                    for f in onlyfiles: 
                        ASM.lib_upload(path.join(lib, f))
        elif VALUESPACE.files != None:
            if len(VALUESPACE.files) == 0:
                VALUESPACE.files = ['all']
            for lib in VALUESPACE.files:
                if lib.lower() == 'all':
                    lib = None
                RESULT= ASM.lib_files(lib)
                for item in RESULT:
                    print(item)
        elif VALUESPACE.list:
            RESULT= ASM.lib_list()
            for item in RESULT:
                print(item)
        elif VALUESPACE.version:
            for lib in VALUESPACE.version:
                print(ASM.lib_version(lib))
        elif VALUESPACE.install != None:
            for lib in VALUESPACE.install:
                RESULT = ASM.lib_install(lib)
                if RESULT == ASM.status_fail:
                    print('Error: no such package - "{}"!'.format(lib))
        elif VALUESPACE.freeze:
            RESULT= ASM.lib_freeze()
            for item in RESULT:
                print(item)
        else:
            PARSER.error('No arguments provided.')

    elif VALUESPACE.command == "cert":
        if VALUESPACE.upload != None:
            for cert in VALUESPACE.upload:
                if cert.endswith('.crt'):
                    ASM.cert_upload(cert)
                else:
                    onlyfiles = [f for f in listdir(cert) if path.isfile(path.join(cert, f))]
                    for f in onlyfiles: 
                        if f.endswith('.crt'):
                            ASM.cert_upload(path.join(cert, f))
        elif VALUESPACE.info:
            print(ASM.cert_info())
        elif VALUESPACE.download != None:
            ASM.download_certificate(VALUESPACE.download)
        elif VALUESPACE.truststore != None:
            ASM.download_truststore(VALUESPACE.truststore)
        elif VALUESPACE.remove != None:
            for cert in VALUESPACE.remove:
                ASM.remove_certificate(cert)
        else:
            PARSER.error('No arguments provided.')



    # elif VALUESPACE.command == "xml":
    #     if VALUESPACE.component:
    #         if VALUESPACE.file:
    #             if VALUESPACE.value:
    #                 for component in VALUESPACE.component:
    #                     RESULT = ASM.set_xml(component, VALUESPACE.file, VALUESPACE.value)
    #                     if RESULT != ASM.status_ok:
    #                         print(RESULT)
    #             else:
    #                 print("Value (-v/--value) must be specified.")
    #         else:
    #             print("File (-f/--file) must be specified.")
    #             sys.exit(1)
    #     else:
    #         print("At least 1 component (-c/--component) must be specified.")
    #         sys.exit(1)
    