# file_system_watch
import os
import re
import hashlib
import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def os_walk_modules(path):
    """Traverse all path and sub directories for found all HTML files."""
    for folder, directories, files in os.walk(path):
        # Skip all folder or files that contains '__'
        if '__' in folder:
            continue

        for f in filter(lambda n: n.endswith(".html"), files):
            yield os.path.join(folder, f)

CODE_REGEX = {
    "code": re.compile( r'(?<=CodiceModulo)[\s]*=[\s]*"(?P<value>[\w\d\-\_]+)' ),
    "extends": re.compile( r'(?<=extends)[\s]*"(?P<value>[^\"]+)"' ),
    # "module": re.compile( r'(?<=codice_modulo=")[\w\d\-\_]+' ),
    "urn": re.compile( r'(?<=Urn)[\s]*=[\s]*"(?P<value>[\w\d\-\_:\.;]+)"' ),
    "child_urn": re.compile( r'(?<=urn_modulo_figlio)[\s]*=[\s]*"(?P<value>[\w\d\-\_:\.;]+)"' ),
    "child_code": re.compile( r'(?<=codice_modulo_figlio)[\s]*=[\s]*"(?P<value>[\w\d\-\_:\.;]+)"' ),
}

def module_parse(path):
    """Return a dictionary that contain the module metadata"""

    meta = {
        "file_path": path,
        "key": hashlib.sha256(path.encode('utf-8')).hexdigest(),
        "folders": [p for p in path.split('modules', 1)[-1].split(os.sep)[:-1] if p],
        "filename": os.path.basename(path),
    }
    text = ""
    with open(path, 'r', encoding="utf8") as f:
        i = 0
        while i < 5 and "{% block title %}" not in text:
            text += f.read(4096)
            i += 1


    for key, regex in CODE_REGEX.items():
        for match in regex.finditer(text):
            if key not in meta:
                meta[key] = []

            meta[key].append(match.groupdict()['value'])

    # Add missing key
    [meta.setdefault(key, None) for key in CODE_REGEX.keys()]

    # Normalization
    for key, item in meta.items():
        if key.startswith('child'):
            continue

        if not isinstance(item, list):
            continue

        if len(item) != 1:
            continue

        meta[key] = item[0]


    return meta

SKIPPING_DIRS = [

]
DATA = []
def parse_dir(path):
    """Read the directory and reset all modules data."""
    logging.debug(f"start parsing {path}")
    # Always search directory modules under the main path.
    if not path.endswith('modules'):
        path = os.path.join(path, "modules")

    if not os.path.exists(path):
        logging.error(f"The {path} doesn't exists")
        raise ValueError(f"The {path} doesn't exists")

    global DATA
    DATA = []
    modules = map(module_parse, os_walk_modules(path))
    for m in modules:
        DATA.append(m)

    logging.debug(f"end parsing.")


class ModuleEventHandler(PatternMatchingEventHandler):
    """Handle filesystem changes and match the modules data to the file system."""
    def on_deleted(self, event):
        module = next(meta for meta in DATA if meta['file_path'] == event.src_path)
        DATA.remove(module)
        logging.debug(f"delete module with urn: {module['urn']}")

    def on_created(self, event):
        module = module_parse(event.src_path)
        DATA.append(module)
        logging.debug(f"added module with urn: {module['urn']}")

    def on_modified(self, event):
        module = next(meta for meta in DATA if meta['file_path'] == event.src_path)
        i = DATA.index(module)
        DATA[i] = module_parse(event.src_path)
        logging.debug(f"updated module with urn: {module['urn']}")

    def on_moved(self, event):
        module = next(meta for meta in DATA if meta['file_path'] == event.src_path)
        i = DATA.index(module)
        DATA[i] = module_parse(event.dest_path)
        logging.debug(f"moved module with urn: {module['urn']}")


def start_observer(path):
    event_handler = ModuleEventHandler(
        patterns=['*.htm', '*.html'],
        ignore_patterns=['.git/**/*'],
        ignore_directories=True
    )
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    return observer


def build_statistics(data):
    df = pd.DataFrame(data)
    count_null_urn = len(df) - df.urn.count()
    count_null_code = len(df) - df.code.count()
    print(f"There are {count_null_code} missing CODE.")

    missing_urn_not_base = df[df.apply(lambda x: x['urn'] is None and x['extends'] == "base.html", axis=1)]
    print(f"There are {missing_urn_not_base.count()} missing URN.")

    # count_null_code_urn = df[df.urn.isnull()][df.code.isnull()].count()
    # print(f"There are {count_null_code_urn} missing both CODE and URN.")

    missing_urn_not_base.to_csv('missing_urn.csv')
    df[df.code.isnull()]['file_path'].to_csv('missing_code.csv')


def start_load(path):
    parse_dir(path)


def recursive_topological_sort(graph, node):
    """perform topo sort on a graph

    return an KeyError if some dependency is missing.

    :arg graph: a dict of list with dependency name.
    :arg node: the node you want calculate the dependencies
    """
    result = []
    seen = set()

    def recursive_helper(node):
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                recursive_helper(neighbor)
        result.insert(0, node)              # this line replaces the result.append line

    recursive_helper(node)
    return result


def build_module_graph():
    data = get_modules()
    graph = {}
    for m in data:
        if 'urn' not in m:
            continue

        if m['child_urn'] is None:
            graph[m['urn']] = []
        else:
            graph[m['urn']] = m['child_urn']

    return graph



def get_modules():
    global DATA
    return DATA


def find_module(key: str):
    global DATA
    if key:
        for m in DATA:
            if m['key'] == key:
                return m

    return None

def find_modules_by_urn(urns: list):
    global DATA
    data = []
    for module in DATA:
        if 'urn' not in module:
            continue

        if module['urn'] in urns:
            data.append(module)

    return data

def get_all_dependencies(urn):
    graph = build_module_graph()
    results = recursive_topological_sort(graph, urn)

    return find_modules_by_urn(results)

def get_all_modules_in_folder(folder):
    global DATA

    return filter(lambda m: '/'.join(m['folders']).startswith(folder), DATA)
