import json
from datetime import date, datetime
from typing import Self, List

import requests
from pydantic import BaseModel, Field, model_validator

from msc_sdk.authenticate import Credential, Authenticate
from msc_sdk.enums import APINamespaces
from msc_sdk.contract.contract import Contract, EffectType, DivisionMethod
from msc_sdk.errors import Unauthorized, ServerError, BillingError
from msc_sdk.position import PositionUR
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import list_float_to_int
from msc_sdk.utils.validators import validate_cnpj


class ContractURData(BaseModel):
    due_date: date
    value_available: float

    class Config:
        validate_assignment = True


class ContractPosition(BaseModel):
    payment_scheme: str
    acquirer: str
    ur_list: List[ContractURData]
    max_due_date: datetime = Field(exclude=True)

    class Config:
        validate_assignment = True

    @model_validator(mode="before")
    def validate(self):
        if self.get("acquirer", None):
            self["acquirer"] = validate_cnpj(self["acquirer"])

        return self

    @classmethod
    def from_position_urs(cls, position_urs: List[PositionUR], payment_scheme: str, acquirer: str) -> Self:
        """
        Generate a new instance of ContractPosition from a list of PositionUR objects, a payment scheme and an acquirer.

        Parameters:
            position_urs (List[PositionUR]): A list of PositionUR objects.
            payment_scheme (str): The payment scheme for the new instance.
            acquirer (str): The acquirer for the new instance.

        Returns:
            Self: A new instance of ContractPosition.
        """
        ur_data_list = []
        max_due_date = datetime.now()

        for ur in position_urs:
            ur_data_list.append(ContractURData(due_date=ur.due_date, value_available=ur.value_available))

            if ur.due_date > max_due_date:
                max_due_date = ur.due_date

        return cls(
            payment_scheme=payment_scheme,
            acquirer=acquirer,
            ur_list=ur_data_list,
            max_due_date=max_due_date,
        )


class ContractPositionList(BaseModel):
    positions: List[ContractPosition] = []
    max_due_date: datetime = Field(default_factory=datetime.now, exclude=True)

    def add_from_position_urs(self, position_urs: List[PositionUR], payment_scheme: str, acquirer: str):
        """
        Generate ContractPositions from PositionURs and append them to the positions list.

        Args:
            position_urs (List[PositionUR]): List of PositionUR objects to create ContractPositions from.
            payment_scheme (str): The payment scheme to use for creating ContractPositions.
            acquirer (str): The acquirer to associate with the ContractPositions.
        """
        positions = ContractPosition.from_position_urs(
            position_urs=position_urs, payment_scheme=payment_scheme, acquirer=acquirer
        )

        if positions.max_due_date > self.max_due_date:
            self.max_due_date = positions.max_due_date

        self.positions.append(positions)

    def model_dump_json(self, *args, **kwargs):
        data = json.loads(super().model_dump_json(*args, **kwargs))

        for position in data["positions"]:
            position["ur_list"] = list_float_to_int(position["ur_list"], ["value_available"])

        return json.dumps(data)


class ContractOwnershipAssignment(Contract):
    @classmethod
    def new(cls, credential: Credential, asset_holder: str, positions: ContractPositionList) -> Self:
        """
        A class method to create a new contract of ownership assignment with detailed information.

        Parameters:
            credential (Credential): The credential used for authentication.
            asset_holder (str): The asset holder's information.
            positions (ContractPositionList): A list of contract positions.

        Returns:
            Self: The newly created contract.
        """
        api_path = "detailed/fixed_amount"

        auth = Authenticate.token(credential)

        payload = dict(
            asset_holder=asset_holder,
            contract_due_date=positions.max_due_date.strftime("%Y-%m-%d"),
            bank_account=credential.model_dump()["bank_account"],
            effect_type=EffectType.OWNERSHIP_ASSIGNMENT.value,
            division_method=DivisionMethod.FIXED_AMOUNT.value,
            positions=json.loads(positions.model_dump_json())["positions"],
        )

        for i in range(5):
            try:
                response = requests.post(
                    url=get_url(APINamespaces.CONTRACTS, api_path),
                    headers=dict(Authorization=f"Bearer {auth.access_token.get_secret_value()}"),
                    json=payload,
                )
                break
            except Exception as e:
                if i == 4:
                    raise e

        if response.status_code == 200:
            response = response.json()

            contract = cls.get_by_key(key=response["key"], credential=credential)

            return contract

        elif response.status_code == 401:
            raise Unauthorized("Wrong credentials")

        elif response.status_code == 402:
            raise BillingError(response.text)

        elif response.status_code >= 500:
            raise ServerError("Server error")

        raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
