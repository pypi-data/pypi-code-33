from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import yaml


@dataclass
class Config:
    basepath: Path
    account: ConfigAccount
    zones: Dict[str, ConfigZone]
    certificates: List[ConfigCertificate]

    @classmethod
    def load(cls, filename: str) -> Config:
        path = Path(filename)
        basepath = path.parent
        with path.open('rt') as fp:
            config = yaml.safe_load(fp)

        return cls(
            basepath=basepath,
            account=ConfigAccount(**config['account']),
            zones={zone['name']: ConfigZone(**zone) for zone in config['zones']},
            certificates=[ConfigCertificate(**cert) for cert in config['certificates']],
        )


@dataclass
class ConfigAccount:
    endpoint: str
    key: str
    contacts: Sequence[str]
    algo: str
    params: Mapping[str, Any]
    accepted_tos: str


@dataclass
class ConfigZone:
    name: str
    server: str
    key: str
    secret: str = field(repr=False)
    algo: str


@dataclass
class ConfigCertificate:
    name: str
    domains: Sequence[str]
    algo: str
    params: Mapping[str, Any]
    on_update: Sequence[str]
