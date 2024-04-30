import enum
from datetime import datetime
from typing import Self, List, Any

import requests
from pydantic import BaseModel, Field

from msc_sdk.authenticate import Credential, Authenticate
from msc_sdk.commons import BankAccount, History
from msc_sdk.config_sdk import ConfigSDK, Environment
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import NotFound, Unauthorized, ServerError
from msc_sdk.recurrence import mock_data
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import dict_float_to_int, dict_int_to_float


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
    msc_integrator: str
    msc_customer: str
    payment_scheme: list[PaymentScheme]
    acquirer: str
    bank_account: BankAccount
    ur_percentage: int = 0
    discount_rate_per_year: float
    contract_key: str = None
    created_at: datetime
    updated_at: datetime = None
    cancelled_at: datetime = None
    history: History

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
        msc_integrator: str,
    ) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            return cls(**mock_data["recurrence_list"][0])

        auth = Authenticate.token(credential)

        body = {
            "asset_holder": asset_holder,
            "acquirer": acquirer,
            "bank_account": bank_account.model_dump(),
            "ur_percentage": ur_percentage,
            "discount_rate_per_year": int(discount_rate_per_year * 100),
            "payment_scheme": payment_scheme,
            "msc_integrator": msc_integrator,
        }

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
            recurrence = cls(**response.json())

            return recurrence

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def get_by_id(cls, credential: Credential, recurrence_id: str, msc_integrator: str = None) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            for recurrence in mock_data["recurrence_list"]:
                if recurrence["id"] == recurrence_id:
                    return cls(**recurrence)

        api_path = "search"

        auth = Authenticate.token(credential)

        param = {"msc_customer": credential.document, "id": recurrence_id}
        if msc_integrator:
            param["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
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

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def get_by_contract_key(cls, credential: Credential, contract_key: str, msc_integrator: str = None) -> Self | None:
        api_path = "search"

        auth = Authenticate.token(credential)

        param = {"msc_customer": credential.document, "contract_key": contract_key}
        if msc_integrator:
            param["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
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

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def cancel(
        cls,
        credential: Credential,
        recurrence_id: str,
        msc_customer: str,
        cancel_reason: RecurrenceCancelReason,
        msc_integrator: str = None,
    ) -> Self:
        api_path = f"cancel/{recurrence_id}"

        auth = Authenticate.token(credential)

        params = {"msc_customer": msc_customer, "cancel_reason": cancel_reason.value}

        if msc_integrator:
            params["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.post(
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

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def update_bank_account(
        cls,
        credential: Credential,
        recurrence_id: str,
        bank_account: BankAccount,
        msc_customer: str,
        msc_integrator: str = None,
    ) -> Self:
        api_path = f"bank-account/{recurrence_id}"

        auth = Authenticate.token(credential)

        params = {"msc_customer": msc_customer}

        if msc_integrator:
            params["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.patch(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    json=bank_account.model_dump(),
                    params=params,
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

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def update_discount_rate_per_year(
        cls,
        credential: Credential,
        recurrence_id: str,
        new_discount_rate_per_year: float,
        msc_customer: str,
        msc_integrator: str = None,
    ) -> Self:
        api_path = f"discount-rate-per-year/{recurrence_id}"

        auth = Authenticate.token(credential)

        params = {"msc_customer": msc_customer, "new_discount_rate": new_discount_rate_per_year}

        if msc_integrator:
            params["msc_integrator"] = msc_integrator

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

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")


class RecurrenceList(BaseModel):
    recurrences: List[Recurrence]

    @classmethod
    def get(cls, credential: Credential, page: int, page_size: int, msc_integrator: str = None) -> Self:
        auth = Authenticate.token(credential)

        params = {"masc_customer": credential.document, "page": page, "page_size": page_size}

        if msc_integrator:
            params["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES),
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

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
