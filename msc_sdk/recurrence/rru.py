import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field

from msc_sdk.authenticate import Credential
from msc_sdk.errors import NotFound
from msc_sdk.recurrence import mock_data


class OperationResume(BaseModel):
    operation_id: str
    operation_date: datetime
    previous_amount: float
    previous_operated_amount_gross: float
    previous_operated_amount_net: float
    amount: float
    operated_amount_gross: float
    operated_amount_net: float

    class Config:
        validate_assignment = True


class RecurrenceReceivableUnit(BaseModel):
    id: str
    recurrence_id: str
    ur_id: str
    asset_holder: str
    acquirer: str
    payment_scheme: str
    due_date: datetime
    amount: float
    operated_amount_gross: float = 0
    operated_amount_net: float = 0
    available_amount: float
    operations: list[OperationResume] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime = None

    class Config:
        validate_assignment = True

    @classmethod
    def get_by_ur_id(cls, credential: Credential, ur_id: str) -> Self:
        # TODO: Implement
        for rru in mock_data["rru_list"]:
            if rru["ur_id"] == ur_id:
                return cls(**rru)

        return NotFound("RRU not found")


class RecurrenceReceivableUnitList(BaseModel):
    rrus: list[RecurrenceReceivableUnit] = Field(default_factory=list)

    @classmethod
    def get_by_recurrence_id(cls, credential: Credential, recurrence_id: str, page: int, page_size: int) -> Self:
        # TODO: Implement
        rru_list = cls()
        found = False
        for rru in mock_data["rru_list"]:
            if rru["recurrence_id"] == recurrence_id:
                found = True
                rru_list.rrus.append(RecurrenceReceivableUnit(**rru))

        if found:
            return rru_list

        return NotFound("RRU not found")
