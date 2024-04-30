from datetime import datetime
from typing import Any, Dict, List, Self

import requests
from pydantic import Field, BaseModel, model_validator

from msc_sdk.authenticate import Credential, Authenticate
from msc_sdk.commons import BankAccount, History
from msc_sdk.config_sdk import Environment, ConfigSDK
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import NotFound, Unauthorized, ServerError
from msc_sdk.recurrence import mock_data
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import dict_int_to_float, dict_string_to_datetime


class Payment(BaseModel):
    amount_paid: float
    bank_account_from: BankAccount
    bank_account_to: BankAccount
    payment_date: datetime
    proof_of_payment: Any = None
    metadata: Dict = None

    class Config:
        validate_assignment = True

    @model_validator(mode="before")
    def from_string_to_datetime(self):
        date_time_field_list = ["payment_date"]
        return dict_string_to_datetime(self, date_time_field_list)

    @model_validator(mode="before")
    def from_int_to_float(self):
        in_field_list = ["amount_paid"]
        in_field_list = [field for field in in_field_list if not isinstance(self.get(field), float)]
        convertor = dict_int_to_float(self, in_field_list)
        return convertor


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

    @model_validator(mode="before")
    def from_string_to_datetime(self):
        date_time_field_list = ["due_date", "payment_due_date"]
        return dict_string_to_datetime(self, date_time_field_list)

    @model_validator(mode="before")
    def from_int_to_float(self):
        in_field_list = ["amount", "amount_due", "discount_amount"]
        in_field_list = [field for field in in_field_list if not isinstance(self.get(field), float)]
        convertor = dict_int_to_float(self, in_field_list)
        return convertor


class Operation(BaseModel):
    id: str = None
    operation_date: datetime
    recurrence_id: str
    asset_holder: str
    msc_customer: str
    msc_integrator: str
    operation_receivable_units: List[OperationReceivableUnit] = Field(default_factory=list)
    amount: float = 0
    amount_due: float = 0
    amount_paid: float = 0
    bank_account: BankAccount
    payments: List[Payment]
    created_at: datetime
    updated_at: datetime = None
    history: History

    @model_validator(mode="before")
    def from_string_to_datetime(self):
        date_time_field_list = ["created_at", "updated_at", "operation_date"]
        return dict_string_to_datetime(self, date_time_field_list)

    @model_validator(mode="before")
    def from_int_to_float(self):
        field_list = ["amount", "amount_due", "amount_paid"]
        in_field_list = [field for field in field_list if not isinstance(self.get(field), float)]
        convertor = dict_int_to_float(self, in_field_list)
        return convertor

    class Config:
        validate_assignment = True

    @classmethod
    def new(cls, credential: Credential, asset_holder: str, recurrence_id: str, bank_account: BankAccount) -> Self:
        # TODO: Implement
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, credential: Credential, operation_id: str, msc_integrator: str = None) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            for operation in mock_data["operation_list"]:
                if operation["id"] == operation_id:
                    return cls(**operation)

            return NotFound("Operation not found")

        api_path = f"operations/{operation_id}"

        auth = Authenticate.token(credential)

        param = {"msc_customer": credential.document}

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
            contract = cls(**response.json())

            return contract

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")

    @classmethod
    def get_by_recurrence_id(cls, credential: Credential, recurrence_id: str, msc_integrator: str = None) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            for operation in mock_data["operation_list"]:
                if operation["recurrence_id"] == recurrence_id:
                    return cls(**operation)

            return NotFound("Operation not found")

        api_path = f"operations/recurrence/{recurrence_id}"

        auth = Authenticate.token(credential)

        param = {"msc_customer": credential.document}

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
            contract = cls(**response.json())

            return contract

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")


class OperationList(BaseModel):
    operations: List[Operation]

    @classmethod
    def get(cls, credential: Credential, page: int, page_size: int, msc_integrator: str = None) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            return cls(operations=mock_data["operation_list"])

        auth = Authenticate.token(credential)

        params = {"masc_customer": credential.document, "page": page, "page_size": page_size}

        if msc_integrator:
            params["msc_integrator"] = msc_integrator

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES, "operations"),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    params={"msc_customer": credential.document, "page": page, "page_size": page_size},
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            # if data.get("operations", None):
            #     data["operations"] = list_float_to_int(data["operations"], ["amount", "amount_due", "amount_paid"])
            #
            # for item in data["operations"]:
            #     item["operation_receivable_units"] = list_float_to_int(item["operation_receivable_units"], ["amount",
            #                                                                                                 "discount_amount",
            #                                                                                                 "amount_due"])
            #
            #     item["payments"] = list_float_to_int(item["payments"], ["amount_paid"])
            contract = cls(operations=response.json().get("operations", []))

            return contract

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
