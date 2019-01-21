# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import os

from .loader import (RulesetStruct, get_ruleset_struct_from_file,
                     get_ruleset_struct_from_fileobj)
from ..checks.check_utils import NotLoadedCheck
from ..constant import EXTS, RULESET_DIRECTORY, RULESET_DIRECTORY_NAME
from ..exceptions import ColinRulesetException
from ..loader import CheckLoader
from ..target import is_compatible

logger = logging.getLogger(__name__)


class Ruleset(object):

    def __init__(self, ruleset_name=None, ruleset_file=None, ruleset=None, checks_paths=None):
        """
        Load ruleset for colin.

        :param ruleset_name: str (name of the ruleset file (without any file extension), default is
                             "default"
        :param ruleset_file: fileobj instance holding ruleset configuration
        :param ruleset: dict, content of a ruleset file
        :param checks_paths: list of str, directories where the checks are present
        """
        self.check_loader = CheckLoader(get_checks_paths(checks_paths))
        if ruleset:
            self.ruleset_struct = RulesetStruct(ruleset)
        elif ruleset_file:
            self.ruleset_struct = get_ruleset_struct_from_fileobj(ruleset_file)
        else:
            logger.debug("Loading ruleset with the name '{}'.".format(ruleset_name))
            ruleset_path = get_ruleset_file(ruleset=ruleset_name)
            self.ruleset_struct = get_ruleset_struct_from_file(ruleset_path)
        if self.ruleset_struct.version not in ["1", 1]:
            raise ColinRulesetException("colin accepts only ruleset version '1'. You provided %r"
                                        % self.ruleset_struct.version)

    def get_checks(self, target_type, tags=None, skips=None):
        """
        Get all checks for given type/tags.

        :param skips: list of str
        :param target_type: TargetType class
        :param tags: list of str
        :return: list of check instances
        """
        skips = skips or []
        result = []
        for check_struct in self.ruleset_struct.checks:
            if check_struct.name in skips:
                continue

            logger.debug("Processing check_struct {}.".format(check_struct))

            usable_targets = check_struct.usable_targets
            if target_type and usable_targets \
                    and target_type.get_compatible_check_class().check_type not in usable_targets:
                logger.info("Skipping... Target type does not match.")
                continue

            try:
                check_class = self.check_loader.mapping[check_struct.name]
                check_instance = check_class()
            except KeyError as ke:
                check_instance = NotLoadedCheck(check_name=check_struct.name,
                                                reason="not found")
                logger.debug("Cannot find a code for the check {}. ({})".format(check_struct.name,
                                                                                ke))
            except Exception as ex:
                check_instance = NotLoadedCheck(check_name=check_struct.name,
                                                reason="not instantiated")
                logger.debug("Cannot instantiate the check {}. ({})".format(check_struct.name,
                                                                            ex))

            if check_struct.tags:
                logger.info("Overriding check's tags %s with the one defined in ruleset: %s",
                            check_instance.tags, check_struct.tags)
                check_instance.tags = check_struct.tags[:]
            if check_struct.additional_tags:
                logger.info("Adding additional tags: %s", check_struct.additional_tags)
                check_instance.tags += check_struct.additional_tags

            if not is_compatible(target_type=target_type, check_instance=check_instance):
                logger.error(
                    "Check '{}' not compatible with the target type: {}".format(
                        check_instance.name, target_type.get_compatible_check_class().check_type))
                raise ColinRulesetException(
                    "Check {} can't be used for target type {}".format(
                        check_instance, target_type.get_compatible_check_class().check_type))

            if tags:
                if not set(tags) < set(check_instance.tags):
                    logger.debug(
                        "Check '{}' not passed the tag control: {}".format(check_instance.name,
                                                                           tags))
                    continue

            # and finally, attach attributes from ruleset to the check instance
            for k, v in check_struct.other_attributes.items():
                # yes, this overrides things; yes, users may easily and severely broke their setup
                setattr(check_instance, k, v)

            result.append(check_instance)
            logger.debug("Check instance {} added.".format(check_instance.name))

        return result


def get_checks_paths(checks_paths=None):
    """
    Get path to checks.

    :param checks_paths: list of str, directories where the checks are present
    :return: list of str (absolute path of directory with checks)
    """
    if checks_paths:
        return [os.path.abspath(x) for x in checks_paths]
    p = os.path.join(__file__, os.pardir, os.pardir, os.pardir, "checks")
    p = os.path.abspath(p)
    return [p]


def get_ruleset_file(ruleset=None):
    """
    Get the ruleset file from name

    :param ruleset: str
    :return: str
    """
    ruleset = ruleset or "default"

    ruleset_dirs = get_ruleset_dirs()
    for ruleset_directory in ruleset_dirs:
        possible_ruleset_files = [os.path.join(ruleset_directory, ruleset + ext) for ext in EXTS]

        for ruleset_file in possible_ruleset_files:
            if os.path.isfile(ruleset_file):
                logger.debug("Ruleset file '{}' found.".format(ruleset_file))
                return ruleset_file

    logger.warning("Ruleset with the name '{}' cannot be found at '{}'."
                   .format(ruleset, ruleset_dirs))
    raise ColinRulesetException("Ruleset with the name '{}' cannot be found.".format(ruleset))


def get_ruleset_dirs():
    """
    Get the directory with ruleset files
    First directory to check:  ./rulesets
    Second directory to check:  $HOME/.local/share/colin/rulesets
    Third directory to check: /usr/local/share/colin/rulesets
    :return: str
    """

    ruleset_dirs = []

    cwd_rulesets = os.path.join(".", RULESET_DIRECTORY_NAME)
    if os.path.isdir(cwd_rulesets):
        logger.debug("Ruleset directory found in current directory ('{}').".format(cwd_rulesets))
        ruleset_dirs.append(cwd_rulesets)

    if "VIRTUAL_ENV" in os.environ:
        venv_local_share = os.path.join(os.environ["VIRTUAL_ENV"],
                                        RULESET_DIRECTORY)
        if os.path.isdir(venv_local_share):
            logger.debug("Virtual env ruleset directory found ('{}').".format(venv_local_share))
            ruleset_dirs.append(venv_local_share)

    local_share = os.path.join(os.path.expanduser("~"),
                               ".local",
                               RULESET_DIRECTORY)
    if os.path.isdir(local_share):
        logger.debug("Local ruleset directory found ('{}').".format(local_share))
        ruleset_dirs.append(local_share)

    usr_local_share = os.path.join("/usr/local", RULESET_DIRECTORY)
    if os.path.isdir(usr_local_share):
        logger.debug("Global ruleset directory found ('{}').".format(usr_local_share))
        ruleset_dirs.append(usr_local_share)

    if not ruleset_dirs:
        msg = "Ruleset directory cannot be found."
        logger.warning(msg)
        raise ColinRulesetException(msg)

    return ruleset_dirs


def get_rulesets():
    """"
    Get available rulesets.
    """
    rulesets_dirs = get_ruleset_dirs()
    ruleset_files = []
    for rulesets_dir in rulesets_dirs:
        for f in os.listdir(rulesets_dir):
            for ext in EXTS:
                file_path = os.path.join(rulesets_dir, f)
                if os.path.isfile(file_path) and f.lower().endswith(ext):
                    ruleset_files.append((f[:-len(ext)], file_path))
    return ruleset_files
