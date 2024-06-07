import enum
from datetime import datetime
from typing import Self, List

import requests
from pydantic import BaseModel, field_validator

from msc_sdk.authenticate import Credential, Authenticate
from msc_sdk.commons import BankAccount
from msc_sdk.config_sdk import ConfigSDK, Environment
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import NotFound, Unauthorized, ServerError
from msc_sdk.recurrence import mock_data
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import dict_float_to_int, dict_int_to_float
from msc_sdk.utils.validators import validate_cnpj


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
    cancel_reason: RecurrenceCancelReason | None = None
    asset_holder: str
    msc_integrator: str | None
    msc_customer: str
    payment_scheme: list[PaymentScheme]
    acquirer: str
    bank_account: BankAccount
    ur_percentage: int = 0
    discount_rate_per_year: float
    contract_key: str = None
    created_at: datetime
    updated_at: datetime | None = None
    cancelled_at: datetime | None = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    @field_validator("asset_holder", "acquirer", "msc_integrator")
    @classmethod
    def validate_cnpj(cls, cnpj: str) -> str:
        if cnpj:
            return validate_cnpj(cnpj)
        return cnpj

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
    ) -> "Recurrence":
        if ConfigSDK.get_config().environment == Environment.DEV:
            return cls(**mock_data["recurrence_list"][0])

        auth = Authenticate.token(credential)

        body = {
            "msc_customer": credential.document,
            "asset_holder": asset_holder,
            "acquirer": acquirer,
            "bank_account": bank_account.model_dump(),
            "ur_percentage": ur_percentage,
            "discount_rate_per_year": discount_rate_per_year,
            "payment_scheme": payment_scheme,
        }

        body = dict_float_to_int(body, ["discount_rate_per_year"])

        for i in range(5):
            try:
                response = requests.post(
                    url=get_url(APINamespaces.RECURRENCES),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    json=body,
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            data = dict_int_to_float(response.json(), ["discount_rate_per_year"])
            recurrence = cls(**data)

            return recurrence

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def get_by_id(cls, credential: Credential, recurrence_id: str) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            for recurrence in mock_data["recurrence_list"]:
                if recurrence["id"] == recurrence_id:
                    return cls(**recurrence)

        auth = Authenticate.token(credential)

        param = {"recurrence_id": recurrence_id}

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params=param,
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            recurrence_json = response.json()
            data = dict_int_to_float(recurrence_json, ["discount_rate_per_year"])
            recurrence = cls(**data)

            return recurrence

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def get_by_contract_key(cls, credential: Credential, contract_key: str) -> Self | None:
        auth = Authenticate.token(credential)

        param = {"msc_customer": credential.document, "contract_key": contract_key}

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params=param,
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            recurrence_json = response.json()
            data = dict_int_to_float(recurrence_json, ["discount_rate_per_year"])
            return cls(**data)

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def cancel(cls, credential: Credential, recurrence_id: str, cancel_reason: RecurrenceCancelReason) -> Self:
        auth = Authenticate.token(credential)

        api_path = f"{recurrence_id}/cancel"
        params = {"cancel_reason": cancel_reason.value}

        for i in range(5):
            try:
                response = requests.patch(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params=params,
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            recurrence = cls(**response.json())

            return recurrence

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def update_bank_account(cls, credential: Credential, recurrence_id: str, bank_account: BankAccount) -> Self:
        auth = Authenticate.token(credential)

        api_path = f"{recurrence_id}/bank-account"

        for i in range(5):
            try:
                response = requests.patch(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    json=bank_account.model_dump(),
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            bank_account = BankAccount(**response.json())

            return bank_account

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def update_discount_rate_per_year(
        cls, credential: Credential, recurrence_id: str, new_discount_rate_per_year: float
    ) -> Self:
        auth = Authenticate.token(credential)

        api_path = f"{recurrence_id}/discount-rate-per-year"
        params = {"new_discount_rate": new_discount_rate_per_year}

        for i in range(5):
            try:
                response = requests.patch(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params=params,
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            recurrence = cls(**response.json())

            return recurrence

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")


class RecurrenceList(BaseModel):
    recurrences: List[Recurrence]

    @classmethod
    def get(cls, credential: Credential, page: int, page_size: int, msc_integrator: str = None) -> Self:
        auth = Authenticate.token(credential)

        api_path = "list"
        params = {"masc_customer": credential.document, "page": page, "page_size": page_size}

        if msc_integrator:
            params["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params={"msc_customer": credential.document, "page": page, "page_size": page_size},
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            recurrence_lis_json = response.json()
            recurrence_list = []
            for recurrence in recurrence_lis_json["recurrences"]:
                data = dict_int_to_float(recurrence, ["discount_rate_per_year"])
                recurrence_list.append(data)

            return cls(recurrences=recurrence_list)

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
