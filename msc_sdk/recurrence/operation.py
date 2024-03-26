from datetime import datetime
from typing import Any, Dict, List, Self

from pydantic import Field, BaseModel

from msc_sdk.authenticate import Credential
from msc_sdk.commons import BankAccount
from msc_sdk.errors import NotFound
from msc_sdk.recurrence import mock_data


class Payment(BaseModel):
    amount_paid: float
    bank_account_from: BankAccount
    bank_account_to: BankAccount
    payment_date: datetime
    proof_of_payment: Any = None
    metadata: Dict = None

    class Config:
        validate_assignment = True


class OperationReceivableUnit(BaseModel):
    ur_id: str
    asset_holder: str
    payment_scheme: str
    acquirer: str
    due_date: datetime
    payment_due_date: datetime
    amount: float
    discount_rate_per_year: float
    discount_rate: float = 0
    discount_amount: float = 0
    amount_due: float = 0

    class Config:
        validate_assignment = True


class Operation(BaseModel):
    id: str = None
    operation_date: datetime
    recurrence_id: str
    asset_holder: str
    operation_receivable_units: List[OperationReceivableUnit] = Field(default_factory=list)
    amount: float = 0
    amount_due: float = 0
    amount_paid: float = 0
    bank_account: BankAccount
    payments: List[Payment] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime = None

    class Config:
        validate_assignment = True

    @classmethod
    def new(cls, credential: Credential, asset_holder: str, recurrence_id: str, bank_account: BankAccount) -> Self:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, credential: Credential, operation_id: str) -> Self:
        # TODO: Implement
        for operation in mock_data["operation_list"]:
            if operation["id"] == operation_id:
                return cls(**operation)

        return NotFound("Operation not found")

    @classmethod
    def get_by_recurrence_id(cls, credential: Credential, recurrence_id: str) -> Self:
        # TODO: Implement
        for operation in mock_data["operation_list"]:
            if operation["recurrence_id"] == recurrence_id:
                return cls(**operation)

        return NotFound("Operation not found")

    def update_payment(self):
        # TODO: Implement
        raise NotImplementedError


class OperationList(BaseModel):
    operations: List[Operation]

    @classmethod
    def get(cls, credential: Credential, page: int, page_size: int) -> Self:
        # TODO: Implement
        return cls(operations=mock_data["operation_list"])
