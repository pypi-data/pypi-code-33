# -*- coding: utf-8 -*-

from .pyjapc import PyJapc
from .rbac_dialog import PasswordEntryDialogue, getPw

__version__ = "2.0.3"

__cmmnbuild_deps__ = [
    "japc",
    "japc-value",
    "japc-ext-cmwrda",
    "japc-ext-cmwrda3",
    "japc-ext-tgm",
    "japc-ext-inca",
    "japc-ext-dirservice",
    "rbac-client",
    "rbac-util",
    "inca-client",
    "slf4j-log4j12",
    "slf4j-api",
    "log4j"
]
