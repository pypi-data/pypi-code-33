"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
from cortex import Cortex
import argparse
import yaml
from .utils import named_dict


class ActionBuildCommand:
    """
    Builds a Cortex action.
    """
    def __init__(self, args):
        parser = argparse.ArgumentParser(description='Build and deploy a Cortex Action',
                                         usage='cortex-build actions [args] [action_name]')
        parser.add_argument('-f', '--file', type=open, default='project.yml')
        parser.add_argument('action_name', nargs='?', type=str)

        opts = parser.parse_args(args)
        project = named_dict(yaml.load(opts.file))

        c = Cortex.client()
        b = c.builder()

        for action in project.actions:
            build = action.build
            if build.runtime == 'python3':
                # If action_name was specified, only build the requested action
                if opts.action_name:
                    if action.name != opts.action_name:
                        continue

                print('Building action: {}'.format(action.name))
                builder = b.action(action.name)

                # Action type: job, daemon, function
                if hasattr(builder, action.type):
                    getattr(builder, action.type)()

                if hasattr(build, 'from_image'):
                    builder.from_image(build.from_image)

                elif hasattr(build, 'from_setup'):
                    s = build.from_setup

                    setup_script = 'setup.py'
                    if hasattr(s, 'setup_script'):
                        setup_script = s.setup_script

                    builder.from_setup(setup_script, s.module, s.function)

                if hasattr(build, 'requirements'):
                    builder.with_requirements(build.requirements)

                kwargs = {}
                if hasattr(build, 'extra'):
                    kwargs = build.extra or {}

                builder.build(**kwargs)


class CortexBuild:
    """
    Provides build functionality for the Cortex SDK
    """
    def __init__(self):
        parser = argparse.ArgumentParser(description='Cortex Build Tool for Python', usage='cortex-build <command>')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        opts = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, opts.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, opts.command)()

    def actions(self):
        """
        Invoke ActionBuildCommand
        """
        ActionBuildCommand(sys.argv[2:])


def main():
    """
    Main function for invoking CortexBuild
    """
    CortexBuild()
