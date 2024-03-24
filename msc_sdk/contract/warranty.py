from enum import Enum

from msc_sdk.contract.contract import Contract


class WarrantyType(str, Enum):
    FIDUCIARY = "fiduciary"
    PLEDGE = "pledge"


class ContractWarranty(Contract):
    warranty_type: str
    warranty_amount: int
