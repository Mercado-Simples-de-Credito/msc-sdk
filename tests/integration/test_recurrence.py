from datetime import datetime

import pytest

from msc_sdk.enums import AccountType
from msc_sdk.recurrence import mock_data
from msc_sdk.recurrence import Operation, OperationList
from msc_sdk.recurrence import RecurrenceList, Recurrence
from msc_sdk.recurrence import RecurrenceReceivableUnitList, RecurrenceReceivableUnit
from msc_sdk.commons import BankAccount
from msc_sdk.recurrence.recurrence import RecurrenceCancelReason
from tests.unit.conftest import setup_config

assert setup_config is not None


@pytest.fixture(scope="module")
def mock() -> dict:
    return mock_data


def test_create_recurrence_with_valid_inputs(credential, mock):
    recurrence_response = Recurrence.new(
        credential,
        asset_holder=mock_data["recurrence_list"][0]["asset_holder"],
        payment_scheme=mock_data["recurrence_list"][0]["payment_scheme"],
        bank_account=mock_data["recurrence_list"][0]["bank_account"],
        acquirer=mock_data["recurrence_list"][0]["acquirer"],
        ur_percentage=mock_data["recurrence_list"][0]["ur_percentage"],
        discount_rate_per_year=mock_data["recurrence_list"][0]["discount_rate_per_year"],
    )

    assert recurrence_response.id is not None
    assert recurrence_response.status == "PENDING"
    assert recurrence_response.asset_holder == mock_data["recurrence_list"][0]["asset_holder"]
    assert recurrence_response.msc_integrator is None
    assert recurrence_response.msc_customer == mock_data["msc_customer"]
    assert recurrence_response.payment_scheme == mock_data["recurrence_list"][0]["payment_scheme"]
    assert recurrence_response.acquirer == mock_data["recurrence_list"][0]["acquirer"]
    assert recurrence_response.bank_account.model_dump() == mock_data["recurrence_list"][0]["bank_account"].model_dump()
    assert recurrence_response.ur_percentage == mock_data["recurrence_list"][0]["ur_percentage"]
    assert recurrence_response.discount_rate_per_year == mock_data["recurrence_list"][0]["discount_rate_per_year"]
    assert recurrence_response.contract_key is not None
    assert isinstance(recurrence_response.created_at, datetime)


def test_get_recurrence_with_valid_inputs(credential, mock):
    new_recurrence = Recurrence.new(
        credential,
        asset_holder=mock_data["recurrence_list"][0]["asset_holder"],
        payment_scheme=mock_data["recurrence_list"][0]["payment_scheme"],
        bank_account=mock_data["recurrence_list"][0]["bank_account"],
        acquirer=mock_data["recurrence_list"][0]["acquirer"],
        ur_percentage=mock_data["recurrence_list"][0]["ur_percentage"],
        discount_rate_per_year=mock_data["recurrence_list"][0]["discount_rate_per_year"],
    )

    get_by_id_response = Recurrence.get_by_id(credential, new_recurrence.id)

    assert get_by_id_response.id == new_recurrence.id
    assert get_by_id_response.status == "PENDING"
    assert get_by_id_response.asset_holder == mock_data["recurrence_list"][0]["asset_holder"]
    assert get_by_id_response.msc_integrator == new_recurrence.msc_integrator
    assert get_by_id_response.msc_customer == mock_data["msc_customer"]
    assert get_by_id_response.payment_scheme == mock_data["recurrence_list"][0]["payment_scheme"]
    assert get_by_id_response.acquirer == mock_data["recurrence_list"][0]["acquirer"]
    assert get_by_id_response.bank_account.model_dump() == mock_data["recurrence_list"][0]["bank_account"].model_dump()
    assert get_by_id_response.ur_percentage == mock_data["recurrence_list"][0]["ur_percentage"]
    assert get_by_id_response.discount_rate_per_year == mock_data["recurrence_list"][0]["discount_rate_per_year"]
    assert get_by_id_response.contract_key == new_recurrence.contract_key
    assert get_by_id_response.created_at.replace(microsecond=0) == new_recurrence.created_at.replace(microsecond=0)

    get_by_contract_key = Recurrence.get_by_contract_key(credential, new_recurrence.contract_key)

    assert get_by_contract_key.id == new_recurrence.id
    assert get_by_contract_key.status == "PENDING"
    assert get_by_contract_key.asset_holder == mock_data["recurrence_list"][0]["asset_holder"]
    assert get_by_contract_key.msc_integrator == new_recurrence.msc_integrator
    assert get_by_contract_key.msc_customer == mock_data["msc_customer"]
    assert get_by_contract_key.payment_scheme == mock_data["recurrence_list"][0]["payment_scheme"]
    assert get_by_contract_key.acquirer == mock_data["recurrence_list"][0]["acquirer"]
    assert get_by_contract_key.bank_account.model_dump() == mock_data["recurrence_list"][0]["bank_account"].model_dump()
    assert get_by_contract_key.ur_percentage == mock_data["recurrence_list"][0]["ur_percentage"]
    assert get_by_contract_key.discount_rate_per_year == mock_data["recurrence_list"][0]["discount_rate_per_year"]
    assert get_by_contract_key.contract_key == new_recurrence.contract_key
    assert get_by_contract_key.created_at.replace(microsecond=0) == new_recurrence.created_at.replace(microsecond=0)


def test_get_recurrence_list_with_valid_inputs(credential, mock):
    new_recurrence = Recurrence.new(
        credential,
        asset_holder=mock_data["recurrence_list"][0]["asset_holder"],
        payment_scheme=mock_data["recurrence_list"][0]["payment_scheme"],
        bank_account=mock_data["recurrence_list"][0]["bank_account"],
        acquirer=mock_data["recurrence_list"][0]["acquirer"],
        ur_percentage=mock_data["recurrence_list"][0]["ur_percentage"],
        discount_rate_per_year=mock_data["recurrence_list"][0]["discount_rate_per_year"],
    )

    get_list_response = RecurrenceList.get(credential, 1, 10)

    assert get_list_response.recurrences[0].id == new_recurrence.id
    assert get_list_response.recurrences[0].status == "PENDING"
    assert get_list_response.recurrences[0].asset_holder == mock_data["recurrence_list"][0]["asset_holder"]
    assert get_list_response.recurrences[0].msc_integrator == new_recurrence.msc_integrator
    assert get_list_response.recurrences[0].msc_customer == mock_data["msc_customer"]
    assert get_list_response.recurrences[0].payment_scheme == mock_data["recurrence_list"][0]["payment_scheme"]
    assert get_list_response.recurrences[0].acquirer == mock_data["recurrence_list"][0]["acquirer"]
    assert (
        get_list_response.recurrences[0].bank_account.model_dump()
        == mock_data["recurrence_list"][0]["bank_account"].model_dump()
    )
    assert get_list_response.recurrences[0].ur_percentage == mock_data["recurrence_list"][0]["ur_percentage"]
    assert (
        get_list_response.recurrences[0].discount_rate_per_year
        == mock_data["recurrence_list"][0]["discount_rate_per_year"]
    )
    assert get_list_response.recurrences[0].contract_key == new_recurrence.contract_key
    assert get_list_response.recurrences[0].created_at.replace(microsecond=0) == new_recurrence.created_at.replace(
        microsecond=0
    )


def test_cancel_recurrence_with_valid_inputs(credential, mock):
    new_recurrence = Recurrence.new(
        credential,
        asset_holder=mock_data["recurrence_list"][0]["asset_holder"],
        payment_scheme=mock_data["recurrence_list"][0]["payment_scheme"],
        bank_account=mock_data["recurrence_list"][0]["bank_account"],
        acquirer=mock_data["recurrence_list"][0]["acquirer"],
        ur_percentage=mock_data["recurrence_list"][0]["ur_percentage"],
        discount_rate_per_year=mock_data["recurrence_list"][0]["discount_rate_per_year"],
    )

    get_list_response = Recurrence.cancel(credential, new_recurrence.id, RecurrenceCancelReason.USER)

    assert get_list_response.id == new_recurrence.id
    assert get_list_response.status == "CANCELLED"
    assert get_list_response.cancel_reason == "USER"
    assert get_list_response.asset_holder == mock_data["recurrence_list"][0]["asset_holder"]
    assert get_list_response.msc_integrator == new_recurrence.msc_integrator
    assert get_list_response.msc_customer == mock_data["msc_customer"]
    assert get_list_response.payment_scheme == mock_data["recurrence_list"][0]["payment_scheme"]
    assert get_list_response.acquirer == mock_data["recurrence_list"][0]["acquirer"]
    assert get_list_response.bank_account.model_dump() == mock_data["recurrence_list"][0]["bank_account"].model_dump()
    assert get_list_response.ur_percentage == mock_data["recurrence_list"][0]["ur_percentage"]
    assert get_list_response.discount_rate_per_year == mock_data["recurrence_list"][0]["discount_rate_per_year"]
    assert get_list_response.contract_key == new_recurrence.contract_key
    assert get_list_response.created_at.replace(microsecond=0) == new_recurrence.created_at.replace(microsecond=0)
    assert isinstance(get_list_response.updated_at, datetime)
    assert isinstance(get_list_response.cancelled_at, datetime)


def test_update_recurrence_bank_account_with_valid_inputs(credential, mock):
    new_recurrence = Recurrence.new(
        credential,
        asset_holder=mock_data["recurrence_list"][0]["asset_holder"],
        payment_scheme=mock_data["recurrence_list"][0]["payment_scheme"],
        bank_account=mock_data["recurrence_list"][0]["bank_account"],
        acquirer=mock_data["recurrence_list"][0]["acquirer"],
        ur_percentage=mock_data["recurrence_list"][0]["ur_percentage"],
        discount_rate_per_year=mock_data["recurrence_list"][0]["discount_rate_per_year"],
    )

    new_bank_account = BankAccount(
        branch="4321",
        account="654321",
        account_digit="9",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="60701190",
        document_type="CNPJ",
        document_number="74634410000120",
    )

    recurrence_response = Recurrence.update_bank_account(credential, new_recurrence.id, new_bank_account)

    assert recurrence_response.id == new_recurrence.id
    assert recurrence_response.status == new_recurrence.status
    assert recurrence_response.asset_holder == new_recurrence.asset_holder
    assert recurrence_response.msc_integrator == new_recurrence.msc_integrator
    assert recurrence_response.msc_customer == new_recurrence.msc_customer
    assert recurrence_response.payment_scheme == new_recurrence.payment_scheme
    assert recurrence_response.acquirer == new_recurrence.acquirer
    assert recurrence_response.bank_account.model_dump() == new_bank_account.model_dump()
    assert recurrence_response.ur_percentage == new_recurrence.ur_percentage
    assert recurrence_response.discount_rate_per_year == new_recurrence.discount_rate_per_year
    assert recurrence_response.contract_key == new_recurrence.contract_key
    assert recurrence_response.created_at.replace(microsecond=0) == new_recurrence.created_at.replace(microsecond=0)
    assert isinstance(recurrence_response.updated_at, datetime)


def test_update_recurrence_discount_rate_with_valid_inputs(credential, mock):
    new_recurrence = Recurrence.new(
        credential,
        asset_holder=mock_data["recurrence_list"][0]["asset_holder"],
        payment_scheme=mock_data["recurrence_list"][0]["payment_scheme"],
        bank_account=mock_data["recurrence_list"][0]["bank_account"],
        acquirer=mock_data["recurrence_list"][0]["acquirer"],
        ur_percentage=mock_data["recurrence_list"][0]["ur_percentage"],
        discount_rate_per_year=mock_data["recurrence_list"][0]["discount_rate_per_year"],
    )

    new_discount_rate = 6

    recurrence_response = Recurrence.update_discount_rate(credential, new_recurrence.id, new_discount_rate)

    assert recurrence_response.id == new_recurrence.id
    assert recurrence_response.status == new_recurrence.status
    assert recurrence_response.asset_holder == new_recurrence.asset_holder
    assert recurrence_response.msc_integrator == new_recurrence.msc_integrator
    assert recurrence_response.msc_customer == new_recurrence.msc_customer
    assert recurrence_response.payment_scheme == new_recurrence.payment_scheme
    assert recurrence_response.acquirer == new_recurrence.acquirer
    assert recurrence_response.bank_account.model_dump() == new_recurrence.bank_account.model_dump()
    assert recurrence_response.ur_percentage == new_recurrence.ur_percentage
    assert recurrence_response.discount_rate_per_year == new_discount_rate
    assert recurrence_response.contract_key == new_recurrence.contract_key
    assert recurrence_response.created_at.replace(microsecond=0) == new_recurrence.created_at.replace(microsecond=0)
    assert isinstance(recurrence_response.updated_at, datetime)


def test_get_operations_list_with_valid_inputs(credential):
    operation_list_response = OperationList.get(
        credential, recurrence_id="47712b51-fe61-4253-b3b4-41205e93f157", page=1, page_size=10
    )

    assert operation_list_response.operations[0].id == "27d736fe-7b67-4183-adac-74957a0fd662"
    assert operation_list_response.operations[0].operation_date == datetime.fromisoformat("2024-06-06T15:04:00.920Z")
    assert operation_list_response.operations[0].recurrence_id == "47712b51-fe61-4253-b3b4-41205e93f157"
    assert operation_list_response.operations[0].msc_customer == "35183811000150"
    assert operation_list_response.operations[0].asset_holder == "15365935000149"
    assert (
        operation_list_response.operations[0].operation_receivable_units[0].ur_id
        == "47712b51-fe61-4253-b3b4-41205e93f159"
    )
    assert operation_list_response.operations[0].operation_receivable_units[0].asset_holder == "15365935000149"
    assert operation_list_response.operations[0].operation_receivable_units[0].payment_scheme == "VCC"
    assert operation_list_response.operations[0].operation_receivable_units[0].acquirer == "01027058000191"
    assert operation_list_response.operations[0].operation_receivable_units[0].due_date == datetime.fromisoformat(
        "2024-07-06T00:00:00.000Z"
    )
    assert operation_list_response.operations[0].operation_receivable_units[
        0
    ].payment_due_date == datetime.fromisoformat("2024-06-06T00:00:00.000Z")
    assert operation_list_response.operations[0].operation_receivable_units[0].amount == 10
    assert operation_list_response.operations[0].operation_receivable_units[0].discount_rate_per_year == 12
    assert operation_list_response.operations[0].operation_receivable_units[0].discount_rate == 1
    assert operation_list_response.operations[0].operation_receivable_units[0].discount_amount == 1
    assert operation_list_response.operations[0].operation_receivable_units[0].amount_due == 9
    assert operation_list_response.operations[0].amount == 10
    assert operation_list_response.operations[0].amount_due == 9
    assert operation_list_response.operations[0].amount_paid == 9
    assert operation_list_response.operations[0].bank_account.branch == "1234"
    assert operation_list_response.operations[0].bank_account.account == "123456"
    assert operation_list_response.operations[0].bank_account.account_digit == "1"
    assert operation_list_response.operations[0].bank_account.account_type == "CC"
    assert operation_list_response.operations[0].bank_account.ispb == "60701190"
    assert operation_list_response.operations[0].bank_account.document_type == "CNPJ"
    assert operation_list_response.operations[0].bank_account.document_number == "74634410000120"
    assert operation_list_response.operations[0].payments[0].amount_paid == 9
    assert operation_list_response.operations[0].payments[0].bank_account.branch == "1234"
    assert operation_list_response.operations[0].payments[0].bank_account.account == "123456"
    assert operation_list_response.operations[0].payments[0].bank_account.account_digit == "1"
    assert operation_list_response.operations[0].payments[0].bank_account.account_type == "CC"
    assert operation_list_response.operations[0].payments[0].bank_account.ispb == "60701190"
    assert operation_list_response.operations[0].payments[0].bank_account.document_type == "CNPJ"
    assert operation_list_response.operations[0].payments[0].bank_account.document_number == "74634410000120"
    assert operation_list_response.operations[0].payments[0].payment_date == datetime.fromisoformat(
        "2024-06-06T00:00:00.000Z"
    )
    assert operation_list_response.operations[0].created_at == datetime.fromisoformat("2024-06-06T15:04:00.920Z")


def test_get_operation_by_id_with_valid_inputs(credential):
    operation_response = Operation.get_by_id(
        credential,
        recurrence_id="47712b51-fe61-4253-b3b4-41205e93f157",
        operation_id="27d736fe-7b67-4183-adac-74957a0fd662",
    )

    assert operation_response.id == "27d736fe-7b67-4183-adac-74957a0fd662"
    assert operation_response.operation_date == datetime.fromisoformat("2024-06-06T15:04:00.920Z")
    assert operation_response.recurrence_id == "47712b51-fe61-4253-b3b4-41205e93f157"
    assert operation_response.msc_customer == "35183811000150"
    assert operation_response.asset_holder == "15365935000149"
    assert operation_response.operation_receivable_units[0].ur_id == "47712b51-fe61-4253-b3b4-41205e93f159"
    assert operation_response.operation_receivable_units[0].asset_holder == "15365935000149"
    assert operation_response.operation_receivable_units[0].payment_scheme == "VCC"
    assert operation_response.operation_receivable_units[0].acquirer == "01027058000191"
    assert operation_response.operation_receivable_units[0].due_date == datetime.fromisoformat(
        "2024-07-06T00:00:00.000Z"
    )
    assert operation_response.operation_receivable_units[0].payment_due_date == datetime.fromisoformat(
        "2024-06-06T00:00:00.000Z"
    )
    assert operation_response.operation_receivable_units[0].amount == 10
    assert operation_response.operation_receivable_units[0].discount_rate_per_year == 12
    assert operation_response.operation_receivable_units[0].discount_rate == 1
    assert operation_response.operation_receivable_units[0].discount_amount == 1
    assert operation_response.operation_receivable_units[0].amount_due == 9
    assert operation_response.amount == 10
    assert operation_response.amount_due == 9
    assert operation_response.amount_paid == 9
    assert operation_response.bank_account.branch == "1234"
    assert operation_response.bank_account.account == "123456"
    assert operation_response.bank_account.account_digit == "1"
    assert operation_response.bank_account.account_type == "CC"
    assert operation_response.bank_account.ispb == "60701190"
    assert operation_response.bank_account.document_type == "CNPJ"
    assert operation_response.bank_account.document_number == "74634410000120"
    assert operation_response.payments[0].amount_paid == 9
    assert operation_response.payments[0].bank_account.branch == "1234"
    assert operation_response.payments[0].bank_account.account == "123456"
    assert operation_response.payments[0].bank_account.account_digit == "1"
    assert operation_response.payments[0].bank_account.account_type == "CC"
    assert operation_response.payments[0].bank_account.ispb == "60701190"
    assert operation_response.payments[0].bank_account.document_type == "CNPJ"
    assert operation_response.payments[0].bank_account.document_number == "74634410000120"
    assert operation_response.payments[0].payment_date == datetime.fromisoformat("2024-06-06T00:00:00.000Z")
    assert operation_response.created_at == datetime.fromisoformat("2024-06-06T15:04:00.920Z")


def test_get_rru_list(credential):
    rru_list_response = RecurrenceReceivableUnitList.get(
        credential, recurrence_id="47712b51-fe61-4253-b3b4-41205e93f157", page=1, page_size=10
    )

    assert rru_list_response.rrus[0].id == "2531a028-25cf-4161-92aa-1e446b8a54f2"
    assert rru_list_response.rrus[0].recurrence_id == "47712b51-fe61-4253-b3b4-41205e93f157"
    assert rru_list_response.rrus[0].ur_id == "47712b51-fe61-4253-b3b4-41205e93f159"
    assert rru_list_response.rrus[0].asset_holder == "15365935000149"
    assert rru_list_response.rrus[0].msc_customer == "35183811000150"
    assert rru_list_response.rrus[0].acquirer == "01027058000191"
    assert rru_list_response.rrus[0].due_date == datetime.fromisoformat("2024-07-06T00:00:00.000Z")
    assert rru_list_response.rrus[0].amount == 10
    assert rru_list_response.rrus[0].total_operated_amount_gross == 10
    assert rru_list_response.rrus[0].total_operated_amount_net == 9
    assert rru_list_response.rrus[0].available_amount == 10
    assert rru_list_response.rrus[0].previous_amount == 0
    assert rru_list_response.rrus[0].previous_operated_amount_gross == 0
    assert rru_list_response.rrus[0].previous_operated_amount_net == 0
    assert rru_list_response.rrus[0].operations == []
    assert rru_list_response.rrus[0].created_at == datetime.fromisoformat("2024-06-06T15:04:00.920Z")
    assert rru_list_response.rrus[0].updated_at is None


def test_get_rru_by_ur_id(credential):
    rru_list_response = RecurrenceReceivableUnit.get(
        credential, rru_id="2531a028-25cf-4161-92aa-1e446b8a54f2", recurrence_id="47712b51-fe61-4253-b3b4-41205e93f157"
    )

    assert rru_list_response.id == "2531a028-25cf-4161-92aa-1e446b8a54f2"
    assert rru_list_response.recurrence_id == "47712b51-fe61-4253-b3b4-41205e93f157"
    assert rru_list_response.ur_id == "47712b51-fe61-4253-b3b4-41205e93f159"
    assert rru_list_response.asset_holder == "15365935000149"
    assert rru_list_response.msc_customer == "35183811000150"
    assert rru_list_response.acquirer == "01027058000191"
    assert rru_list_response.due_date == datetime.fromisoformat("2024-07-06T00:00:00.000Z")
    assert rru_list_response.amount == 10
    assert rru_list_response.total_operated_amount_gross == 10
    assert rru_list_response.total_operated_amount_net == 9
    assert rru_list_response.available_amount == 10
    assert rru_list_response.previous_amount == 0
    assert rru_list_response.previous_operated_amount_gross == 0
    assert rru_list_response.previous_operated_amount_net == 0
    assert rru_list_response.operations == []
    assert rru_list_response.created_at == datetime.fromisoformat("2024-06-06T15:04:00.920Z")
    assert rru_list_response.updated_at is None
