import yaml
from typing import Optional, Any, Dict
from pathlib import Path
from miracle import Acl
from .logging import get_logger

ALLOW = 'allow'

log = get_logger(__name__)
acl: Optional[Acl] = None
config_cache: Optional[Dict[str, Any]] = None


def load_config_file(config_file: str) -> dict:
    """ Load a config file and populate the ACL """
    global config_cache

    conf_path = Path(config_file).expanduser().resolve()

    config_cache = None

    with conf_path.open() as _file:
        config_cache = yaml.load(_file.read())

    if not isinstance(config_cache, dict):
        raise ValueError("Invalid ACL config format")

    log.debug("Loaded config file from {}.".format(conf_path))

    return config_cache


def build_acl(config: Dict[str, Any]) -> Acl:
    """ Build the ACL from config """
    global acl
    acl = Acl()

    log.debug("Building ACL from config...")

    if 'roles' in config:
        assert isinstance(config['roles'], dict), "Invalid roles config"
        acl.add_roles(config['roles'].keys())
        for k, v in config['roles'].items():
            log.debug("Adding role {}...".format(k))
            acl.add_role(k)
            if len(v) > 0:
                for res in v:
                    log.debug("Adding resource {}...".format(res))
                    acl.add_resource(res)

                    log.debug("Adding ALLOW")
                    acl.add_permission(res, ALLOW)

                    log.debug("Granting ALLOW for {} to resource {}...".format(
                        k,
                        res
                    ))
                    acl.grant(k, res, ALLOW)

    return acl


def load_acl_config(config_file: str) -> Acl:
    """ Initialize all the things """
    global acl, config_cache

    if config_cache is None:
        load_config_file(config_file)

    assert config_cache is not None, (
        "config cache was not populated. This is a bug."
    )

    if acl is None:
        build_acl(config_cache)

    return acl


def check_allowed(path: str, ip: Optional[str] = None) -> bool:
    """ Check if the request is allowed """

    log.debug("check_allowed: {} (IP: {})".format(path, ip))

    if config_cache is None or acl is None:
        raise Exception("acl.load() must be called first")

    path_parts = path.split('/')

    """ The ACL is processed partially. So if /get is allowed, /get/whatever
    will also be allowed.  So we check each part individually starting from the
    highest level and proceeding down against the whitelist ACL.
    """
    for i in range(1, len(path_parts) + 1):

        path_partial = '/'.join(path_parts[:i])

        if acl.check('public', path_partial, ALLOW):
            log.debug("{} ALLOWED public".format(path))
            return True

        if acl.check(ip, path_partial, ALLOW):
            log.debug("{} ALLOWED for {}".format(path, ip))
            return True

    log.info("{} BLOCKED".format(path))
    return False
