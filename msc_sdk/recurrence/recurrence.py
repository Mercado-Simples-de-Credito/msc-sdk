import enum
from datetime import datetime
from typing import Self, List

from pydantic import BaseModel

from msc_sdk.authenticate import Credential
from msc_sdk.commons import BankAccount
from msc_sdk.errors import NotFound
from msc_sdk.recurrence import mock_data


class RecurrenceStatus(enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class RecurrenceCancelReason(enum.Enum):
    USER = "USER"
    BILLING = "BILLING"
    FRAUD = "FRAUD"


class PaymentScheme(enum.Enum):
    VISA = "VCC"
    MASTERCARD = "MCC"
    ELO = "ECC"


class Recurrence(BaseModel):
    id: str = None
    status: RecurrenceStatus = RecurrenceStatus.PENDING
    cancel_reason: RecurrenceCancelReason = None
    asset_holder: str
    payment_scheme: list[PaymentScheme]
    acquirer: str
    bank_account: BankAccount
    ur_percentage: int = 0
    discount_rate_per_year: float
    contract_key: str = None
    created_at: datetime
    updated_at: datetime = None
    cancelled_at: datetime = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    @classmethod
    def new(
        cls,
        credential: Credential,
        asset_holder: str,
        acquirer: str,
        bank_account: BankAccount,
        ur_percentage: int,
        discount_rate_per_year: float,
        payment_scheme: list[PaymentScheme],
    ) -> Self:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, credential: Credential, recurrence_id: str) -> Self:
        # TODO: Implement
        for recurrence in mock_data["recurrence_list"]:
            if recurrence["id"] == recurrence_id:
                return cls(**recurrence)

        return NotFound("Recurrence not found")

    @classmethod
    def get_by_contract_key(cls, credential: Credential, contract_key: str, msc_customer: str) -> Self | None:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def cancel(
        cls,
        credential: Credential,
        recurrence_id: str,
        msc_customer: str,
        cancel_reason: RecurrenceCancelReason,
        msc_integrator: str = None,
    ) -> Self:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def update_percentage_ur(
        cls,
        credential: Credential,
        recurrence_id: str,
        new_percentage: int,
        msc_customer: str,
        msc_integrator: str = None,
    ) -> Self:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def update_bank_account(
        cls,
        credential: Credential,
        recurrence_id: str,
        bank_account: BankAccount,
        msc_customer: str,
        msc_integrator: str = None,
    ) -> Self:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def update_discount_rate_per_year(
        cls,
        credential: Credential,
        recurrence_id: str,
        new_discount_rate_per_year: float,
        msc_customer: str,
        msc_integrator: str = None,
    ) -> Self:
        # TODO: Implement
        raise NotImplementedError


class RecurrenceList(BaseModel):
    recurrences: List[Recurrence]

    @classmethod
    def get(cls, credential: Credential, page: int, page_size: int) -> Self:
        # TODO: Implement
        return cls(recurrences=mock_data["recurrence_list"])
