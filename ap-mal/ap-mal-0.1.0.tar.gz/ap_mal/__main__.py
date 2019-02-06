#!/usr/bin/env python3

import logging
import json
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime

from ap_mal import DEBUG, AnimePlanet, MyAnimeList, parse_args


# TODO actual features
#   Export raw to file
#   Import from file to MAL
#   Export from AP -> Import to MAL
#   Export raw from MAL to file
#   Export to a normalized format from AP
#   Export to a normalized format from MAL

# TODO for fun
#   Use click for CLI

log = logging.getLogger('CLI')


def main():
    args = parse_args()
    fmt = "%(asctime)s %(message)s"
    time_format = "%H:%M:%S"  # %Y-%m-%d
    lvl: int = logging.DEBUG if DEBUG > 0 else logging.INFO
    logging.basicConfig(level=lvl, format=fmt, datefmt=time_format)
    if args.IMPORT:
        import_data(args.IMPORT, args.LIST_TYPE, args.FILE)
    else:
        export_data(args.EXPORT, args.LIST_TYPE)


def import_data(service_name: str, list_type: str, filepath: Optional[str]):
    # TODO: there's gotta be a better way
    if service_name in ['ap', 'anime-planet']:
        service = AnimePlanet()
    else:
        service = MyAnimeList()
    if filepath:
        file = Path(filepath).resolve()
        if not file.is_file():
            print(f"Non-existant or invalid input file: {file.name}")
            sys.exit(1)
        data = json.loads(file.read_text(encoding='utf-8'))
    else:
        # TODO: there's gotta be a better way
        if service_name in ['ap', 'anime-planet']:  # Reversal
            remote = MyAnimeList()
        else:
            remote = AnimePlanet()
        # TODO: handle all
        data = remote.export_list(list_type)
    # TODO: handle all
    service.import_list(list_type, data)


def export_data(service_name: str, list_type: str):
    # TODO: there's gotta be a better way
    if service_name in ['ap', 'anime-planet']:
        service = AnimePlanet()
    else:
        service = MyAnimeList()
    # TODO: handle all in a better way
    list_types = ['anime', 'manga'] if list_type == 'all' else [list_type]
    for lt in list_types:
        data = service.export_list(lt)
        tstamp = str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        filename = f'{service.ALIAS}_{lt}_{tstamp}.json'
        file = Path.cwd() / Path(filename)
        log.info(f"Saving {lt} list export data to file {file.name}...")
        with file.open('w', encoding='utf-8') as fp:
            json.dump(data, fp)
    log.info("Finished exporting!")


if __name__ == '__main__':
    main()
