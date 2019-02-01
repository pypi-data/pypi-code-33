from typing import NamedTuple
from skale.contracts import BaseContract
from skale.utils.contract_types import ContractTypes


class ContractInfo(NamedTuple):
    name: str
    contract_name: str
    contract_class: BaseContract
    type: ContractTypes
    upgradable: bool
