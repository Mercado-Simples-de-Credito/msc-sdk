import pytest

from msc_sdk.contract.contract import DivisionMethod, EffectType, EffectStrategy
from msc_sdk.contract import ContractOwnershipAssignment
from msc_sdk.contract.ownership_assignment import ContractPositionList
from msc_sdk.position.position import PositionUR


@pytest.fixture
def test_data():
    contract_position = ContractPositionList()
    contract_position.add_from_position_urs(
        position_urs=[
            PositionUR(due_date="2030-01-01", ur_amount="10.00", value_available="10.00"),
            PositionUR(due_date="2030-02-01", ur_amount="20.00", value_available="20.00"),
        ],
        payment_scheme="MCC",
        acquirer="41548447000187",
    )
    contract_position.add_from_position_urs(
        position_urs=[
            PositionUR(due_date="2030-01-01", ur_amount="30.00", value_available="30.00"),
            PositionUR(due_date="2030-02-01", ur_amount="40.00", value_available="40.00"),
        ],
        payment_scheme="VCC",
        acquirer="41548447000187",
    )

    balance_due = 0
    for position in contract_position.positions:
        for ur in position.ur_list:
            balance_due += ur.value_available

    return dict(
        asset_holder="44226946000146",
        contract_position=contract_position,
        balance_due=balance_due,
    )


def test_new_ownership_assignment_with_valid_inputs(credential, test_data):
    contract = ContractOwnershipAssignment.new(credential, test_data["asset_holder"], test_data["contract_position"])

    assert contract.key is not None
    assert contract.asset_holder == test_data["asset_holder"]
    assert contract.bank_account == credential.bank_account
    assert contract.effect_type == EffectType.OWNERSHIP_ASSIGNMENT
    assert contract.division_method == DivisionMethod.FIXED_AMOUNT
    assert contract.effect_strategy == EffectStrategy.SPECIFIC
    assert contract.contract_due_date == test_data["contract_position"].max_due_date
    assert contract.balance_due == test_data["balance_due"]
