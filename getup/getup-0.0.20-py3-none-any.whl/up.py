#!/usr/bin/env python3

import os
import sys
import json
import pathlib
import importlib

app_dir = os.environ.get("GETUP_APP_DIR")
if app_dir:
    APP_DIR = pathlib.Path(app_dir)
    sys.path.append(str(APP_DIR.resolve()))
    sys.path.append(str(APP_DIR.resolve().parent))


CUR_DIR = pathlib.Path(os.getcwd())
sys.path.append(str(CUR_DIR.resolve()))
sys.path.append(str(CUR_DIR.resolve().parent))


def create_url_patterns(paths):
    """
    For given iterable of url, module path pairs creates urlpatterns
    Imports given path's package and uses path's last part as the view callable
    This allows defining URL patterns using JSON.
    """
    from django.urls import path

    urlpatterns = (
        path(url, importlib.import_module(importable_module_path)[0])
        for url, importable_module_path in paths
    )
    return tuple(urlpatterns)


def import_app():
    
    if os.environ.get('GETUP_APP_PATH'):
        imported = importlib.import_module(os.environ.get('GETUP_APP_PATH'))
        return None
    else:
        app_path = sys.argv[1]
        if os.path.exists(app_path + '.py'):
            imported = importlib.import_module(app_path)
        return app_path

def main():
    
    app_path = import_app()
    if app_path:
        sys.argv.remove(app_path)
        os.environ['GETUP_APP_PATH'] = app_path

    from django.core.management import execute_from_command_line

    # Delegate to Django management
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
