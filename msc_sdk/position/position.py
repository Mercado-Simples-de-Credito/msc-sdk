from datetime import datetime
from enum import Enum
from typing import List, Self

import requests
from pydantic import BaseModel, model_validator, Field

from msc_sdk.authenticate import Authenticate, Credential
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import Unauthorized, ServerError, NotFound, BillingError
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import dict_int_to_float, list_int_to_float
from msc_sdk.utils.validators import validate_cnpj


class RequestPositionType(str, Enum):
    SINGLE = "single"
    RECURRENT = "recurrent"


class RequestPositionUR(BaseModel):
    payment_scheme: str
    acquirer: str
    error_message: str = None

    class Config:
        validate_assignment = True


class RequestPositionURList(BaseModel):
    optin: List[RequestPositionUR]

    class Config:
        validate_assignment = True

    def delete_one(self, payment_scheme: str, acquirer: str):
        self.optin = [ur for ur in self.optin if ur.payment_scheme != payment_scheme or ur.acquirer != acquirer]

    def update_errors(self, payment_scheme: str, acquirer: str, error_message: str):
        for ur in self.optin:
            if ur.payment_scheme == payment_scheme and ur.acquirer == acquirer:
                ur.error_message = error_message


class PositionUR(BaseModel):
    due_date: datetime
    ur_amount: float
    value_available: float

    class Config:
        validate_assignment = True


class Position(BaseModel):
    key: str
    asset_holder: str
    payment_scheme: str
    acquirer: str
    update_position_start: datetime = None
    update_position_end: datetime
    key_optin_tag: str = None
    ur_list_resume: List[PositionUR] = None
    total_ur_amount: float = 0
    total_value_available: float = 0
    ur_list_last_update: datetime = None
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    @model_validator(mode="before")
    def validate(self):
        if self.get("asset_holder", None):
            self["asset_holder"] = validate_cnpj(self["asset_holder"])

        return self

    @classmethod
    def get_by_data(
        cls,
        credential: Credential,
        payment_scheme: str,
        acquirer: str,
        asset_holder: str,
    ) -> Self:
        api_path = "report"
        auth = Authenticate.token(credential)

        response = requests.get(
            url=get_url(APINamespaces.POSITIONS, api_path),
            headers={"Authorization": f"Bearer {auth.access_token.get_secret_value()}"},
            params={
                "payment_scheme": payment_scheme,
                "acquirer": acquirer,
                "asset_holder": asset_holder,
                "msc_customer": credential.document,
            },
        )

        if response.status_code == 200:
            data = dict_int_to_float(response.json(), ["total_ur_amount", "total_value_available"])

            data["ur_list_resume"] = list_int_to_float(data["ur_list_resume"], ["ur_amount", "value_available"])

            return cls(**data)

        elif response.status_code == 204:
            raise NotFound("Contract not found")

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")


def request_position_report(
    credential: Credential,
    asset_holder: str,
    request_position_type: RequestPositionType,
    request_position_ur_list: RequestPositionURList,
    update_position_end: datetime = None,
) -> tuple[List[Position], RequestPositionURList]:
    """
    Create request for position report.

    Args:
        credential (Credential): Credential object
        asset_holder (str): CNPJ of the asset holder
        request_position_type (RequestPositionType): Type of request
        request_position_ur_list (RequestPositionURList): List of URs
        update_position_end (datetime, optional): End date of the recurrent position. Defaults to None.

    Returns:
        tuple[List[Position], RequestPositionURList]: List of positions and RequestPositionURList with
        requested positions errors
    """
    api_path = "report"
    auth = Authenticate.token(credential)

    payload = {
        "asset_holder": asset_holder,
        "type": request_position_type.value,
        "optin": request_position_ur_list.model_dump()["optin"],
    }

    if request_position_type == RequestPositionType.RECURRENT:
        if not update_position_end:
            raise ValueError("Recurrent positions must have an end date 'update_position_end'")
        payload["update_position_end"] = update_position_end.strftime("%Y-%m-%d")

    response = requests.post(
        url=get_url(APINamespaces.POSITIONS, api_path),
        headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
        json=payload,
    )

    if response.status_code == 200:
        response = response.json()

        positions = []
        if response.get("optin", None):
            for item in response["optin"]:
                if item["success"]:
                    positions.append(
                        Position.get_by_data(
                            credential=credential,
                            payment_scheme=item["payment_scheme"],
                            acquirer=item["acquirer"],
                            asset_holder=asset_holder,
                        )
                    )
                    request_position_ur_list.delete_one(
                        payment_scheme=item["payment_scheme"], acquirer=item["acquirer"]
                    )
                else:
                    request_position_ur_list.update_errors(
                        payment_scheme=item["payment_scheme"],
                        acquirer=item["acquirer"],
                        error_message=item["msg_err"],
                    )

        return positions, request_position_ur_list

    elif response.status_code == 401:
        raise Unauthorized("Wrong credentials")

    elif response.status_code == 402:
        raise BillingError(response.text)

    elif response.status_code >= 500:
        raise ServerError("Server error")

    raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
