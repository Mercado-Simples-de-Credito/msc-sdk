import json
from datetime import datetime
from enum import Enum
from typing import Any, List, Self

import requests
from pydantic import BaseModel, model_validator, Field

from msc_sdk.authenticate import Authenticate, Credential
from msc_sdk.commons import BankAccount
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import Unauthorized, ServerError, NotFound
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.validators import validate_cnpj
from msc_sdk.utils.converters import (
    dict_int_to_float,
    list_int_to_float,
    dict_float_to_int,
    list_float_to_int,
)


class EffectStrategy(str, Enum):
    SPECIFIC = "specific"
    CUSTOM = "custom"


class EffectType(str, Enum):
    WARRANTY = "warranty"
    OWNERSHIP_ASSIGNMENT = "ownershipAssignment"
    PAWN = "pawn"


class DivisionMethod(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixedAmount"


class ContractUR(BaseModel):
    ur_id: str = None
    acquirer: str = None
    payment_scheme: str = None
    due_date: datetime
    effect_amount: float = 0
    committed_effect_amount: float = 0
    effect_priority: int = 0

    class Config:
        populate_by_name = True
        validate_assignment = True

    @model_validator(mode="before")
    def validate(self):
        if self.get("acquirer", None):
            self["acquirer"] = validate_cnpj(self["acquirer"])

        return self


class Contract(BaseModel):
    key: str = None
    asset_holder: str
    bank_account: BankAccount
    signature_date: datetime = Field(default_factory=datetime.now)
    contract_due_date: datetime
    effect_type: EffectType
    division_method: DivisionMethod
    effect_strategy: EffectStrategy
    balance_due: float = 0
    committed_effect_amount: float = 0
    percentage_value: int = 0
    process_key_tag: str = None
    ur_list: List[ContractUR]
    ur_list_last_update: datetime | None = None
    status: Any = None
    created_on: datetime
    updated_on: datetime | None = None
    canceled_on: datetime | None = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    @model_validator(mode="before")
    def validate(self):
        if self.get("asset_holder", None):
            self["asset_holder"] = validate_cnpj(self["asset_holder"])

        self["ur_list"] = self["ur_list"] if "ur_list" in self else []

        return self

    @classmethod
    def get_by_key(cls, key: str, credential: Credential) -> Self:
        """
        A class method to retrieve contract by key using.

        Parameters:
            key (str): The key to retrieve the contract.
            credential (Credential): The credential object used for authentication.

        Returns:
            Self: An instance of the class with the retrieved data.

        Raises:
            NotFound: If the contract is not found.
            Unauthorized: If the credentials are incorrect.
            ServerError: If a server error occurs.
            Exception: For unexpected errors including the response status code and text.
        """
        auth = Authenticate.token(credential)

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.CONTRACTS),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params=dict(key=key, msc_customer=credential.document),
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            data = dict_int_to_float(response.json(), ["balance_due", "committed_effect_amount"])

            if data.get("ur_list", None):
                data["ur_list"] = list_int_to_float(data["ur_list"], ["effect_amount", "committed_effect_amount"])

            return cls(**data)

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def cancel_by_key(cls, key: str, credential: Credential) -> Self:
        """
        A class method to cancel a contract by its key using the provided credential.

        Parameters:
            key (str): The key of the contract to be canceled.
            credential (Credential): The credential used for authentication.

        Returns:
            Self: The canceled contract.

        Raises:
            NotFound: If the contract is not found.
            Unauthorized: If the credentials are incorrect.
            ServerError: If a server error occurs.
            Exception: If an unexpected error occurs.
        """
        api_path = "cancel"

        auth = Authenticate.token(credential)

        for i in range(5):
            try:
                response = requests.patch(
                    url=get_url(APINamespaces.CONTRACTS, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    json=dict(key=key),
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            contract = cls.get_by_key(key=key, credential=credential)

            return contract

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    def model_dump_json(self, *args, **kwargs):
        data = json.loads(super().model_dump_json(*args, **kwargs))

        data = dict_float_to_int(data, ["balance_due", "committed_effect_amount"])

        if data.get("ur_list", None):
            data["ur_list"] = list_float_to_int(data["ur_list"], ["effect_amount", "committed_effect_amount"])

        return json.dumps(data)
