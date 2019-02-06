import subprocess, os
from pathlib import Path
from .files import determine_project_path

def run_script(script, d):
    # Get the path from this file
    target_script = determine_project_path() + '/../bash/' + script + '.sh'
    # Execute the script
    my_env = os.environ.copy()

    for key, value in d.items():
        my_env[key] = value

    return subprocess.call([target_script], env=my_env)
