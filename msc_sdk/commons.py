from typing import Any

from pydantic import BaseModel, Field

from msc_sdk.enums import AccountType


class BankAccount(BaseModel):
    branch: str
    account: str
    account_digit: str = Field(alias="accountDigit")
    account_type: AccountType = Field(alias="accountType")
    ispb: str
    document_type: str = Field("CNPJ", alias="documentType")
    document_number: str = Field(alias="documentNumber")

    class Config:
        validate_assignment = True
        use_enum_values = True
        populate_by_name = True


class History(BaseModel):
    updated_data: list[Any] = []
    snapshot: dict = {}

    class Config:
        validate_assignment = True
