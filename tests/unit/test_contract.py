import uuid
from datetime import datetime

import pytest

from msc_sdk.contract.contract import DivisionMethod, EffectType, EffectStrategy
from msc_sdk.enums import APINamespaces
from msc_sdk.contract import ContractOwnershipAssignment
from msc_sdk.contract.ownership_assignment import ContractPositionList
from msc_sdk.position.position import PositionUR
from msc_sdk.utils.api_tools import get_url


@pytest.fixture
def test_data():
    contract_position = ContractPositionList()
    contract_position.add_from_position_urs(
        position_urs=[
            PositionUR(due_date="2030-01-01", ur_amount="10.00", value_available="10.00"),
            PositionUR(due_date="2030-02-01", ur_amount="20.00", value_available="20.00"),
        ],
        payment_scheme="MCC",
        acquirer="1027058000191",
    )
    contract_position.add_from_position_urs(
        position_urs=[
            PositionUR(due_date="2030-01-01", ur_amount="30.00", value_available="30.00"),
            PositionUR(due_date="2030-02-01", ur_amount="40.00", value_available="40.00"),
        ],
        payment_scheme="VCC",
        acquirer="1027058000191",
    )

    balance_due = 0
    for position in contract_position.positions:
        for ur in position.ur_list:
            balance_due += ur.value_available

    return dict(
        asset_holder="89785141000170",
        contract_position=contract_position,
        balance_due=balance_due,
    )


def test_new_ownership_assignment_with_valid_inputs(credential, test_data, requests_mock):
    key = str(uuid.uuid4())

    post_response_data = {"key": key, "asset_holder": test_data["asset_holder"]}
    requests_mock.post(
        get_url(APINamespaces.CONTRACTS, "detailed/fixed_amount"),
        json=post_response_data,
        status_code=200,
    )

    get_parms_data = f"?key={key}&msc_customer={credential.document}"

    get_response_data = {
        "key": key,
        "asset_holder": test_data["asset_holder"],
        "bank_account": credential.bank_account.model_dump(),
        "signature_date": datetime.now().isoformat(),
        "contract_due_date": test_data["contract_position"].max_due_date.isoformat(),
        "effect_type": EffectType.OWNERSHIP_ASSIGNMENT.value,
        "division_method": DivisionMethod.FIXED_AMOUNT.value,
        "effect_strategy": EffectStrategy.SPECIFIC.value,
        "balance_due": int(test_data["balance_due"] * 100),
        "created_on": datetime.now().isoformat(),
    }

    url = get_url(APINamespaces.CONTRACTS) + get_parms_data

    requests_mock.get(url, json=get_response_data, status_code=200)

    contract = ContractOwnershipAssignment.new(credential, test_data["asset_holder"], test_data["contract_position"])

    assert contract.key is not None
    assert contract.asset_holder == test_data["asset_holder"]
    assert contract.bank_account == credential.bank_account
    assert contract.effect_type == EffectType.OWNERSHIP_ASSIGNMENT
    assert contract.division_method == DivisionMethod.FIXED_AMOUNT
    assert contract.effect_strategy == EffectStrategy.SPECIFIC
    assert contract.contract_due_date == test_data["contract_position"].max_due_date
    assert contract.balance_due == test_data["balance_due"]


def test_get_ownership_assignment_with_valid_inputs(credential, test_data, requests_mock):
    key = str(uuid.uuid4())

    get_parms_data = f"?key={key}&msc_customer={credential.document}"

    get_response_data = {
        "key": key,
        "asset_holder": test_data["asset_holder"],
        "bank_account": credential.bank_account.model_dump(),
        "signature_date": datetime.now().isoformat(),
        "contract_due_date": test_data["contract_position"].max_due_date.isoformat(),
        "effect_type": EffectType.OWNERSHIP_ASSIGNMENT.value,
        "division_method": DivisionMethod.FIXED_AMOUNT.value,
        "effect_strategy": EffectStrategy.SPECIFIC.value,
        "balance_due": int(test_data["balance_due"] * 100),
        "committed_effect_amount": 5000,
        "process_key_tag": "test_tag",
        "ur_list": [],
        "ur_list_last_update": datetime.now().isoformat(),
        "status": "COMPLETED",  # TODO: Add other statuses
        "created_on": datetime.now().isoformat(),
        "updated_on": datetime.now().isoformat(),
        "canceled_on": datetime.now().isoformat(),
    }

    url = get_url(APINamespaces.CONTRACTS) + get_parms_data

    requests_mock.get(url, json=get_response_data, status_code=200)

    contract = ContractOwnershipAssignment.get_by_key(key=key, credential=credential)

    assert contract.key is not None
    assert contract.asset_holder == test_data["asset_holder"]
    assert contract.bank_account == credential.bank_account
    assert contract.signature_date.isoformat() == get_response_data["signature_date"]
    assert contract.contract_due_date.isoformat() == get_response_data["contract_due_date"]
    assert contract.effect_type == EffectType.OWNERSHIP_ASSIGNMENT
    assert contract.division_method == DivisionMethod.FIXED_AMOUNT
    assert contract.effect_strategy == EffectStrategy.SPECIFIC
    assert contract.balance_due == test_data["balance_due"]
    assert contract.committed_effect_amount == get_response_data["committed_effect_amount"] / 100
    assert contract.process_key_tag == get_response_data["process_key_tag"]
    assert contract.ur_list == get_response_data["ur_list"]
    assert contract.ur_list_last_update.isoformat() == get_response_data["ur_list_last_update"]
    assert contract.status == get_response_data["status"]
    assert contract.created_on.isoformat() == get_response_data["created_on"]
    assert contract.updated_on.isoformat() == get_response_data["updated_on"]
    assert contract.canceled_on.isoformat() == get_response_data["canceled_on"]
