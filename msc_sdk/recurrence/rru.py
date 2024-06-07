import uuid
from datetime import datetime
from typing import Self

import requests
from pydantic import BaseModel, Field, model_validator

from msc_sdk.authenticate import Credential, Authenticate
from msc_sdk.config_sdk import ConfigSDK, Environment
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import NotFound, Unauthorized, ServerError
from msc_sdk.recurrence import mock_data
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import dict_string_to_datetime, dict_int_to_float, list_int_to_float


class OperationResume(BaseModel):
    operation_id: str
    operation_date: datetime
    previous_ur_amount: float
    previous_total_operated_amount_gross: float
    previous_total_operated_amount_net: float
    ur_amount: float
    operated_amount_gross: float
    operated_amount_net: float
    total_operated_amount_gross: float
    total_operated_amount_net: float

    class Config:
        validate_assignment = True


class RecurrenceReceivableUnit(BaseModel):
    id: str
    recurrence_id: str
    ur_id: str
    asset_holder: str
    msc_integrator: str | None = None
    msc_customer: str
    acquirer: str
    payment_scheme: str
    due_date: datetime
    amount: float
    total_operated_amount_gross: float
    total_operated_amount_net: float
    available_amount: float
    previous_amount: float
    previous_operated_amount_gross: float
    previous_operated_amount_net: float
    operations: list[OperationResume] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        validate_assignment = True

    @classmethod
    def get(cls, credential: Credential, rru_id: str, recurrence_id: str) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            for rru in mock_data["rru_list"]:
                if rru["rru_id"] == rru_id:
                    return cls(**rru)

        api_path = f"{recurrence_id}/rrus/{rru_id}"

        auth = Authenticate.token(credential)

        for i in range(5):
            try:
                response = requests.get(
                    url=get_url(APINamespaces.RECURRENCES, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            rru_json = response.json()

            data = dict_int_to_float(
                rru_json,
                [
                    "amount",
                    "total_operated_amount_gross",
                    "total_operated_amount_net",
                    "available_amount",
                    "previous_amount",
                    "previous_operated_amount_gross",
                    "previous_operated_amount_net",
                ],
            )

            if data.get("operations", None):
                data["operations"] = list_int_to_float(
                    data["operations"],
                    [
                        "previous_ur_amount",
                        "previous_total_operated_amount_gross",
                        "previous_total_operated_amount_net",
                        "ur_amount",
                        "operated_amount_gross",
                        "operated_amount_net",
                        "total_operated_amount_gross",
                        "total_operated_amount_net",
                    ],
                )

            return cls(**data)

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")


class RecurrenceReceivableUnitList(BaseModel):
    rrus: list[RecurrenceReceivableUnit] = Field(default_factory=list)

    @classmethod
    def get(
        cls, credential: Credential, recurrence_id: str, page: int, page_size: int, msc_integrator: str = None
    ) -> Self:
        if ConfigSDK.get_config().environment == Environment.DEV:
            rru_list = cls()
            found = False
            for rru in mock_data["rru_list"]:
                if rru["recurrence_id"] == recurrence_id:
                    found = True
                    rru_list.rrus.append(RecurrenceReceivableUnit(**rru))

            if found:
                return rru_list

        api_path = f"{recurrence_id}/rrus/list"

        auth = Authenticate.token(credential)

        param = {"page": page, "page_size": page_size}

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
            rru_list_json = response.json()["rrus"]

            rru_list = []
            for rru in rru_list_json:
                data = dict_int_to_float(
                    rru,
                    [
                        "amount",
                        "total_operated_amount_gross",
                        "total_operated_amount_net",
                        "available_amount",
                        "previous_amount",
                        "previous_operated_amount_gross",
                        "previous_operated_amount_net",
                    ],
                )

                if data.get("operations", None):
                    data["operations"] = list_int_to_float(
                        data["operations"],
                        [
                            "previous_ur_amount",
                            "previous_total_operated_amount_gross",
                            "previous_total_operated_amount_net",
                            "ur_amount",
                            "operated_amount_gross",
                            "operated_amount_net",
                            "total_operated_amount_gross",
                            "total_operated_amount_net",
                        ],
                    )

                rru_list.append(RecurrenceReceivableUnit(**data))

            return cls(rrus=rru_list)

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        else:
            raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
