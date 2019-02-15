"""Sweat CLI to provision the FS from env vars (CI tool)."""

import cli2
import os


@cli2.option('verbose', help='Verbose output', color=cli2.GREEN, alias='v')
@cli2.option('dryrun', help='Do not actually touch the fs', color=cli2.GREEN)
def write(name, path, fmod='640', dmod='750'):
    """
    Write an environment variable into a file.

    Usage example:

        env2fs write SSH_KEY ~/.ssh/id_rsa fmod=600 dmod=700

    Note that the missing dollar sign is intendent to prevent evaluation from
    the parent shell itself).

    The above example writes the contents of the $SSH_KEY environment variable
    into ~/.ssh/id_rsa, with a mode of 600 and 700 for any parent directory
    that will be automatically created if necessary.
    """
    if name not in os.environ:
        raise cli2.Cli2Exception(f'${name} not found')

    dryrun = console_script.parser.options.get('dryrun', False)
    verbose = console_script.parser.options.get('verbose', False)

    path_parts = os.path.abspath(path).split('/')[:-1]
    for num, part in enumerate(path_parts, start=1):
        dst = os.path.join('/', *path_parts[:num])
        if dst == '/':
            continue

        if os.path.exists(dst):
            if os.path.isdir(dst):
                if verbose:
                    yield f'{dst} already present'
            else:
                raise cli2.Cli2Exception(
                    f'{cli2.RED}{dst} exists and not a dir{cli2.RESET}')
        else:
            if verbose or dryrun:
                yield f'mkdir {dst} && chmod {dmod} {dst}'

            if not dryrun:
                os.mkdir(dst, int(dmod, 8))

    if verbose or dryrun:
        yield f'echo ${name} > {path} && chmod {fmod} {path}'

    if not dryrun:
        with open(path, 'w+') as fh:
            fh.write(os.getenv(name))
        os.chmod(path, int(fmod, 8))
        yield f'{cli2.GREEN}Wrote {cli2.RESET}: {path}'


console_script = cli2.ConsoleScript(
    __doc__, default_command='write'
).add_module('env2fs')
