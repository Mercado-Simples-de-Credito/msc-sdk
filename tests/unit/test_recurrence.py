import random
import uuid
from datetime import datetime

import pytest

from msc_sdk.enums import APINamespaces, AccountType
from msc_sdk.recurrence import mock_data
from msc_sdk.recurrence import Operation, OperationList
from msc_sdk.recurrence import RecurrenceList, Recurrence
from msc_sdk.recurrence import RecurrenceReceivableUnitList, RecurrenceReceivableUnit
from msc_sdk.commons import BankAccount
from msc_sdk.recurrence.recurrence import RecurrenceCancelReason
from msc_sdk.utils.api_tools import get_url
from msc_sdk.utils.converters import dict_float_to_int, dict_datetime_to_str
from tests.unit.conftest import setup_config

assert setup_config is not None

history = {"updated_data": [], "snapshot": {}}

recurrence_missing_fields_from_mock = {
    "status": "ACTIVE",
    "ur_percentage": 100,
    "contract_key": str(uuid.uuid4()),
    "msc_integrator": "string",
    "msc_customer": "string",
    "history": history,
}

operations_resume_rru_mock = {
    "operation_id": "string",
    "operation_date": "2024-04-30T03:30:03.215Z",
    "previous_ur_amount": round(random.uniform(10.00, 1000.00), 2),
    "previous_total_operated_amount_gross": round(random.uniform(10.00, 1000.00), 2),
    "previous_total_operated_amount_net": round(random.uniform(10.00, 1000.00), 2),
    "ur_amount": round(random.uniform(10.00, 1000.00), 2),
    "operated_amount_gross": round(random.uniform(10.00, 1000.00), 2),
    "operated_amount_net": round(random.uniform(10.00, 1000.00), 2),
    "total_operated_amount_gross": round(random.uniform(10.00, 1000.00), 2),
    "total_operated_amount_net": round(random.uniform(10.00, 1000.00), 2),
}


@pytest.fixture(scope="module")
def recurrence_list_mock(mock: list = mock_data["recurrence_list"]) -> dict:
    merged_dict_list = []
    for item in mock:
        if item.get("bank_account"):
            if isinstance(item["bank_account"], BankAccount):
                item["bank_account"] = item["bank_account"].model_dump()

        if item.get("created_at"):
            if isinstance(item["created_at"], datetime):
                item["created_at"] = item["created_at"].isoformat()

        merged_dict = {**item, **recurrence_missing_fields_from_mock}
        merged_dict_list.append(merged_dict)
    return dict(recurrences=merged_dict_list)


@pytest.fixture(scope="module")
def recurrence_mock(mock: list = mock_data["recurrence_list"]) -> dict:
    first_recurrence_data = mock[0]
    if first_recurrence_data.get("bank_account"):
        if isinstance(first_recurrence_data["bank_account"], BankAccount):
            first_recurrence_data["bank_account"] = first_recurrence_data["bank_account"].model_dump()
    if first_recurrence_data.get("created_at"):
        if isinstance(first_recurrence_data["created_at"], datetime):
            first_recurrence_data["created_at"] = first_recurrence_data["created_at"].isoformat()

    return {**first_recurrence_data, **recurrence_missing_fields_from_mock}


@pytest.fixture(scope="module")
def canceled_recurrence_mock_response(mock: list = mock_data["recurrence_list"]) -> dict:
    first_recurrence_data = mock[0]
    if first_recurrence_data.get("bank_account"):
        if isinstance(first_recurrence_data["bank_account"], BankAccount):
            first_recurrence_data["bank_account"] = first_recurrence_data["bank_account"].model_dump()
    if first_recurrence_data.get("created_at"):
        if isinstance(first_recurrence_data["created_at"], datetime):
            first_recurrence_data["created_at"] = first_recurrence_data["created_at"].isoformat()

    first_recurrence_data["cancelled_at"] = datetime.now().isoformat()
    first_recurrence_data["status"] = "CANCELLED"
    first_recurrence_data["cancel_reason"] = "BILLING"

    return {**first_recurrence_data, **recurrence_missing_fields_from_mock}


@pytest.fixture(scope="module")
def update_bank_account_mock() -> BankAccount:
    return BankAccount(
        branch="1234",
        account="123456",
        account_digit="1",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="12345678900",
        document_type="CNPJ",
        document_number="74634410000120",
    )


@pytest.fixture(scope="module")
def operations_list_mock(mock: list = mock_data["operation_list"]) -> dict:
    operations_mock = {"operations": []}
    for operation in mock:
        operation["payments"] = []
        operation = dict_float_to_int(operation, ["amount", "amount_due", "amount_paid"])
        if operation.get("created_at", None):
            if isinstance(operation["created_at"], datetime):
                operation["created_at"] = operation["created_at"].isoformat()

        if operation.get("updated_at", None):
            if isinstance(operation["updated_at"], datetime):
                operation["updated_at"] = operation["updated_at"].isoformat()

        if operation.get("operation_date", None):
            if isinstance(operation["operation_date"], datetime):
                operation["operation_date"] = operation["operation_date"].isoformat()

        if operation.get("bank_account"):
            if isinstance(operation["bank_account"], BankAccount):
                operation["bank_account"] = operation["bank_account"].model_dump()

        for receivable_unit in operation.get("operation_receivable_units", []):
            receivable_unit = dict_float_to_int(receivable_unit, ["amount", "discount_amount", "amount_due"])

            if receivable_unit.get("due_date", None):
                if isinstance(receivable_unit["due_date"], datetime):
                    receivable_unit["due_date"] = receivable_unit["due_date"].isoformat()

            if receivable_unit.get("payment_due_date", None):
                if isinstance(receivable_unit["payment_due_date"], datetime):
                    receivable_unit["payment_due_date"] = receivable_unit["payment_due_date"].isoformat()

        for payments in operation.get("payments", []):
            if payments.get("payment_date", None):
                if isinstance(payments["payment_date"], datetime):
                    payments["payment_date"] = payments["payment_date"].isoformat()
        operation["history"] = history
        operation["msc_integrator"] = "test_integrator"
        operation["msc_customer"] = "test_customer"
        operations_mock["operations"].append(operation)

    return operations_mock


@pytest.fixture(scope="module")
def rru_list_mock(mock: list = mock_data["rru_list"]) -> dict:
    rru_mock_list = {"rrus": []}
    for rru in mock:
        field_list = [
            "amount",
            "operated_amount_gross",
            "operated_amount_net",
            "operated_amount_net",
            "available_amount",
        ]
        rru = dict_float_to_int(rru, field_list)

        date_time_field_list = ["due_date", "created_at", "updated_at"]
        operation_resume_field_list = [
            "previous_ur_amount",
            "previous_total_operated_amount_gross",
            "previous_total_operated_amount_net",
            "ur_amount",
            "operated_amount_gross",
            "operated_amount_net",
            "total_operated_amount_gross",
            "total_operated_amount_net",
        ]
        date_time_field_list_operations = ["operation_date"]
        for index, items in enumerate(rru["operations"]):
            rru["operations"][index] = dict_datetime_to_str(items, date_time_field_list_operations)

        rru["operations"] = [dict_float_to_int(operations_resume_rru_mock, operation_resume_field_list)]

        rru = dict_datetime_to_str(rru, date_time_field_list)
        rru_mock_list["rrus"].append(rru)

    return rru_mock_list


def test_create_recurrence_with_valid_inputs(credential, recurrence_mock, requests_mock):
    url = get_url(APINamespaces.RECURRENCES)

    requests_mock.post(url, json=recurrence_mock, status_code=200)

    recurrence_response = Recurrence.new(
        credential,
        asset_holder=recurrence_mock["asset_holder"],
        payment_scheme=recurrence_mock["payment_scheme"],
        bank_account=BankAccount(**recurrence_mock["bank_account"]),
        acquirer=recurrence_mock["acquirer"],
        ur_percentage=recurrence_mock["ur_percentage"],
        discount_rate_per_year=recurrence_mock["discount_rate_per_year"],
        msc_integrator=str(uuid.uuid4()),
    )

    assert recurrence_response.id == recurrence_mock["id"]
    assert recurrence_response.status == recurrence_mock["status"]
    assert recurrence_response.asset_holder == recurrence_mock["asset_holder"]
    assert recurrence_response.msc_integrator == recurrence_mock["msc_integrator"]
    assert recurrence_response.msc_customer == recurrence_mock["msc_customer"]
    assert recurrence_response.payment_scheme == recurrence_mock["payment_scheme"]
    assert recurrence_response.acquirer == recurrence_mock["acquirer"]
    assert recurrence_response.bank_account.model_dump() == recurrence_mock["bank_account"]
    assert recurrence_response.ur_percentage == recurrence_mock["ur_percentage"]
    assert recurrence_response.discount_rate_per_year == recurrence_mock["discount_rate_per_year"]
    assert recurrence_response.contract_key == recurrence_mock["contract_key"]
    assert recurrence_response.created_at == datetime.fromisoformat(recurrence_mock["created_at"])


def test_get_recurrence_list_with_valid_inputs(credential, recurrence_list_mock, requests_mock):
    get_params_data = f"?msc_customer={credential.document}"

    url = get_url(APINamespaces.RECURRENCES) + get_params_data

    requests_mock.get(url, json=recurrence_list_mock, status_code=200)

    recurrence = RecurrenceList.get(credential, page=1, page_size=10)
    assert recurrence.recurrences[0].id == recurrence_list_mock["recurrences"][0]["id"]
    assert recurrence.recurrences[0].status == recurrence_list_mock["recurrences"][0]["status"]
    assert recurrence.recurrences[0].asset_holder == recurrence_list_mock["recurrences"][0]["asset_holder"]
    assert recurrence.recurrences[0].msc_integrator == recurrence_list_mock["recurrences"][0]["msc_integrator"]
    assert recurrence.recurrences[0].msc_customer == recurrence_list_mock["recurrences"][0]["msc_customer"]
    assert recurrence.recurrences[0].payment_scheme == recurrence_list_mock["recurrences"][0]["payment_scheme"]
    assert recurrence.recurrences[0].acquirer == recurrence_list_mock["recurrences"][0]["acquirer"]
    assert recurrence.recurrences[0].bank_account.model_dump() == recurrence_list_mock["recurrences"][0]["bank_account"]
    assert recurrence.recurrences[0].ur_percentage == recurrence_list_mock["recurrences"][0]["ur_percentage"]
    assert (
        recurrence.recurrences[0].discount_rate_per_year
        == recurrence_list_mock["recurrences"][0]["discount_rate_per_year"] / 100
    )
    assert recurrence.recurrences[0].contract_key == recurrence_list_mock["recurrences"][0]["contract_key"]
    assert recurrence.recurrences[0].created_at == datetime.fromisoformat(
        recurrence_list_mock["recurrences"][0]["created_at"]
    )


def test_get_recurrence_with_valid_inputs(credential, recurrence_mock, requests_mock):
    id = recurrence_mock["id"]

    get_params_data = f"?msc_customer={credential.document}&id={id}"

    url = get_url(APINamespaces.RECURRENCES, "search") + get_params_data

    requests_mock.get(url, json=recurrence_mock, status_code=200)

    recurrence = Recurrence.get_by_id(credential, id)

    assert recurrence.id == recurrence_mock["id"]
    assert recurrence.status == recurrence_mock["status"]
    assert recurrence.asset_holder == recurrence_mock["asset_holder"]
    assert recurrence.msc_integrator == recurrence_mock["msc_integrator"]
    assert recurrence.msc_customer == recurrence_mock["msc_customer"]
    assert recurrence.payment_scheme == recurrence_mock["payment_scheme"]
    assert recurrence.acquirer == recurrence_mock["acquirer"]
    assert recurrence.bank_account.model_dump() == recurrence_mock["bank_account"]
    assert recurrence.ur_percentage == recurrence_mock["ur_percentage"]
    assert recurrence.discount_rate_per_year == recurrence_mock["discount_rate_per_year"] / 100
    assert recurrence.contract_key == recurrence_mock["contract_key"]
    assert recurrence.created_at == datetime.fromisoformat(recurrence_mock["created_at"])


def test_get_recurrence_with_contract_key(credential, recurrence_mock, requests_mock):
    contract_key = recurrence_mock["contract_key"]

    get_params_data = f"?msc_customer={credential.document}&contract_key={contract_key}"

    url = get_url(APINamespaces.RECURRENCES, "search") + get_params_data

    requests_mock.get(url, json=recurrence_mock, status_code=200)

    recurrence = Recurrence.get_by_contract_key(credential, contract_key)

    assert recurrence.id == recurrence_mock["id"]
    assert recurrence.status == recurrence_mock["status"]
    assert recurrence.asset_holder == recurrence_mock["asset_holder"]
    assert recurrence.msc_integrator == recurrence_mock["msc_integrator"]
    assert recurrence.msc_customer == recurrence_mock["msc_customer"]
    assert recurrence.payment_scheme == recurrence_mock["payment_scheme"]
    assert recurrence.acquirer == recurrence_mock["acquirer"]
    assert recurrence.bank_account.model_dump() == recurrence_mock["bank_account"]
    assert recurrence.ur_percentage == recurrence_mock["ur_percentage"]
    assert recurrence.discount_rate_per_year == recurrence_mock["discount_rate_per_year"] / 100
    assert recurrence.contract_key == recurrence_mock["contract_key"]
    assert recurrence.created_at == datetime.fromisoformat(recurrence_mock["created_at"])


def test_cancel_recurrence_with_valid_inputs(credential, canceled_recurrence_mock_response, requests_mock):
    recurrence_id = canceled_recurrence_mock_response["id"]

    get_params_data = f"?msc_customer={credential.document}&cancel_reason=BILLING"
    url = get_url(APINamespaces.RECURRENCES, f"cancel/{recurrence_id}") + get_params_data

    requests_mock.post(url, json=canceled_recurrence_mock_response, status_code=200)

    recurrence = Recurrence.cancel(
        credential, recurrence_id, msc_customer=credential.document, cancel_reason=RecurrenceCancelReason.BILLING
    )

    assert recurrence.id == canceled_recurrence_mock_response["id"]
    assert recurrence.status == canceled_recurrence_mock_response["status"]
    assert recurrence.asset_holder == canceled_recurrence_mock_response["asset_holder"]
    assert recurrence.msc_integrator == canceled_recurrence_mock_response["msc_integrator"]
    assert recurrence.msc_customer == canceled_recurrence_mock_response["msc_customer"]
    assert recurrence.payment_scheme == canceled_recurrence_mock_response["payment_scheme"]
    assert recurrence.acquirer == canceled_recurrence_mock_response["acquirer"]
    assert recurrence.bank_account.model_dump() == canceled_recurrence_mock_response["bank_account"]
    assert recurrence.ur_percentage == canceled_recurrence_mock_response["ur_percentage"]
    assert recurrence.discount_rate_per_year == canceled_recurrence_mock_response["discount_rate_per_year"]
    assert recurrence.contract_key == canceled_recurrence_mock_response["contract_key"]
    assert recurrence.created_at == datetime.fromisoformat(canceled_recurrence_mock_response["created_at"])


def test_update_recurrence_bank_account_with_valid_inputs(
    credential, update_bank_account_mock, requests_mock, recurrence_mock
):
    recurrence_id = recurrence_mock["id"]
    recurrence_mock["bank_account"] = update_bank_account_mock.model_dump()

    get_params_data = f"?msc_customer={credential.document}"
    url = get_url(APINamespaces.RECURRENCES, f"bank-account/{recurrence_id}") + get_params_data

    requests_mock.patch(url, json=update_bank_account_mock.model_dump(), status_code=200)

    bank_account = Recurrence.update_bank_account(
        credential, recurrence_id, msc_customer=credential.document, bank_account=update_bank_account_mock
    )

    assert bank_account == update_bank_account_mock


def test_update_recurrence_discount_rate_with_valid_inputs(credential, requests_mock, recurrence_mock):
    recurrence_id = recurrence_mock["id"]
    new_discount_rate_per_year = 40

    recurrence_mock["discount_rate_per_year"] = new_discount_rate_per_year
    get_params_data = f"?msc_customer={credential.document}&new_discount_rate={new_discount_rate_per_year}"
    url = get_url(APINamespaces.RECURRENCES, f"discount-rate-per-year/{recurrence_id}") + get_params_data

    requests_mock.patch(url, json=recurrence_mock, status_code=200)

    recurrence = Recurrence.update_discount_rate_per_year(
        credential,
        recurrence_id,
        msc_customer=credential.document,
        new_discount_rate_per_year=new_discount_rate_per_year,
    )

    assert recurrence.discount_rate_per_year == new_discount_rate_per_year

    assert recurrence.id == recurrence_mock["id"]
    assert recurrence.status == recurrence_mock["status"]
    assert recurrence.asset_holder == recurrence_mock["asset_holder"]
    assert recurrence.msc_integrator == recurrence_mock["msc_integrator"]
    assert recurrence.msc_customer == recurrence_mock["msc_customer"]
    assert recurrence.payment_scheme == recurrence_mock["payment_scheme"]
    assert recurrence.acquirer == recurrence_mock["acquirer"]
    assert recurrence.bank_account.model_dump() == recurrence_mock["bank_account"]
    assert recurrence.ur_percentage == recurrence_mock["ur_percentage"]
    assert recurrence.discount_rate_per_year == recurrence_mock["discount_rate_per_year"]
    assert recurrence.contract_key == recurrence_mock["contract_key"]
    assert recurrence.created_at == datetime.fromisoformat(recurrence_mock["created_at"])


def test_get_operations_list_with_valid_inputs(credential, requests_mock, operations_list_mock):
    get_params_data = f"?msc_customer={credential.document}&page=1&page_size=10"

    url = get_url(APINamespaces.RECURRENCES, "operations") + get_params_data

    requests_mock.get(url, json=operations_list_mock, status_code=200)

    operation_list = OperationList.get(credential, page=1, page_size=10)

    # Operation
    assert operation_list.operations[0].id == operations_list_mock["operations"][0]["id"]
    assert operation_list.operations[0].operation_date == datetime.fromisoformat(
        operations_list_mock["operations"][0]["operation_date"]
    )
    assert operation_list.operations[0].recurrence_id == operations_list_mock["operations"][0]["recurrence_id"]
    assert operation_list.operations[0].msc_integrator == operations_list_mock["operations"][0]["msc_integrator"]
    assert operation_list.operations[0].msc_customer == operations_list_mock["operations"][0]["msc_customer"]
    assert operation_list.operations[0].amount == operations_list_mock["operations"][0]["amount"] / 100
    assert operation_list.operations[0].amount_due == operations_list_mock["operations"][0]["amount_due"] / 100
    assert operation_list.operations[0].amount_paid == operations_list_mock["operations"][0]["amount_paid"] / 100
    assert (
        operation_list.operations[0].bank_account.model_dump() == operations_list_mock["operations"][0]["bank_account"]
    )  # noqa

    assert operation_list.operations[0].created_at == datetime.fromisoformat(
        operations_list_mock["operations"][0]["created_at"]
    )

    assert operation_list.operations[0].payments == []

    # Operation Receivable Units
    receivable_units = operation_list.operations[0].operation_receivable_units
    receivable_units_mock = operations_list_mock["operations"][0]["operation_receivable_units"]

    assert receivable_units[0].ur_id == receivable_units_mock[0]["ur_id"]
    assert receivable_units[0].asset_holder == receivable_units_mock[0]["asset_holder"]
    assert receivable_units[0].payment_scheme == receivable_units_mock[0]["payment_scheme"]
    assert receivable_units[0].acquirer == receivable_units_mock[0]["acquirer"]
    assert receivable_units[0].due_date == datetime.fromisoformat(receivable_units_mock[0]["due_date"])
    assert receivable_units[0].payment_due_date == datetime.fromisoformat(receivable_units_mock[0]["payment_due_date"])
    assert receivable_units[0].amount == receivable_units_mock[0]["amount"] / 100
    assert receivable_units[0].discount_rate_per_year == receivable_units_mock[0]["discount_rate_per_year"]
    assert receivable_units[0].discount_rate == receivable_units_mock[0]["discount_rate"]
    assert receivable_units[0].discount_amount == receivable_units_mock[0]["discount_amount"] / 100
    assert receivable_units[0].amount_due == receivable_units_mock[0]["amount_due"] / 100


def test_get_operation_by_id_with_valid_inputs(credential, requests_mock, operations_list_mock):
    operation = operations_list_mock["operations"][0]

    get_params_data = f"?msc_customer={credential.document}"
    url = get_url(APINamespaces.RECURRENCES, f"operations/{operation['id']}") + get_params_data

    requests_mock.get(url, json=operation, status_code=200)

    operation_response = Operation.get_by_id(credential, operation_id=operation["id"])

    assert operation_response.id == operation["id"]
    assert operation_response.operation_date == datetime.fromisoformat(operation["operation_date"])
    assert operation_response.msc_integrator == operation["msc_integrator"]
    assert operation_response.msc_customer == operation["msc_customer"]
    assert operation_response.recurrence_id == operation["recurrence_id"]
    assert operation_response.amount == operation["amount"] / 100
    assert operation_response.amount_due == operation["amount_due"] / 100
    assert operation_response.amount_paid == operation["amount_paid"] / 100
    assert operation_response.bank_account.model_dump() == operation["bank_account"]
    assert operation_response.created_at == datetime.fromisoformat(operation["created_at"])
    assert operation_response.payments == []


def test_get_operation_by_recurrence_id_with_valid_inputs(credential, requests_mock, operations_list_mock):
    operation = operations_list_mock["operations"][1]

    get_params_data = f"?msc_customer={credential.document}"

    url = get_url(APINamespaces.RECURRENCES, f"operations/recurrence/{operation['recurrence_id']}") + get_params_data

    requests_mock.get(url, json=operation, status_code=200)

    operation_response = Operation.get_by_recurrence_id(credential, recurrence_id=operation["recurrence_id"])

    assert operation_response.id == operation["id"]
    assert operation_response.operation_date == datetime.fromisoformat(operation["operation_date"])
    assert operation_response.recurrence_id == operation["recurrence_id"]
    assert operation_response.msc_integrator == operation["msc_integrator"]
    assert operation_response.msc_customer == operation["msc_customer"]
    assert operation_response.amount == operation["amount"] / 100
    assert operation_response.amount_due == operation["amount_due"] / 100
    assert operation_response.amount_paid == operation["amount_paid"] / 100
    assert operation_response.bank_account.model_dump() == operation["bank_account"]
    assert operation_response.created_at == datetime.fromisoformat(operation["created_at"])
    assert operation_response.payments == []


def test_get_rru_by_ur_id(credential, requests_mock, rru_list_mock):
    rru = rru_list_mock["rrus"][0]

    url = get_url(APINamespaces.RECURRENCES) + f"{rru['recurrence_id']}/receivable-units/{rru['ur_id']}"

    requests_mock.get(url, json=rru, status_code=200)

    recurrence_response = RecurrenceReceivableUnit.get_by_ur_id(
        credential, recurrence_id=rru["recurrence_id"], ur_id=rru["ur_id"]
    )
    print(rru)
    assert recurrence_response.id == rru["id"]
    assert recurrence_response.recurrence_id == rru["recurrence_id"]
    assert recurrence_response.ur_id == rru["ur_id"]
    assert recurrence_response.asset_holder == rru["asset_holder"]
    assert recurrence_response.msc_integrator == rru["asset_holder"]
    assert recurrence_response.msc_customer == rru["asset_holder"]
    assert recurrence_response.acquirer == rru["acquirer"]
    assert recurrence_response.payment_scheme == rru["payment_scheme"]
    assert recurrence_response.due_date == datetime.fromisoformat(rru["due_date"])
    assert recurrence_response.amount == rru["amount"] / 100
    assert recurrence_response.total_operated_amount_gross == rru["total_operated_amount_gross"] / 100
    assert recurrence_response.total_operated_amount_net == rru["total_operated_amount_net"] / 100
    assert recurrence_response.available_amount == rru["available_amount"] / 100
    assert recurrence_response.created_at == datetime.fromisoformat(rru["created_at"])
    assert recurrence_response.previous_amount == rru["previous_amount"] / 100
    assert recurrence_response.previous_operated_amount_gross == rru["previous_operated_amount_gross"] / 100
    assert recurrence_response.previous_operated_amount_net == rru["previous_operated_amount_net"] / 100

    assert recurrence_response.operations[0].operation_id == rru["operations"][0]["operation_id"]
    assert recurrence_response.operations[0].operation_date == datetime.fromisoformat(
        rru["operations"][0]["operation_date"]
    )
    assert recurrence_response.operations[0].previous_ur_amount == rru["operations"][0]["previous_ur_amount"] / 100
    assert (
        recurrence_response.operations[0].previous_total_operated_amount_gross
        == rru["operations"][0]["previous_total_operated_amount_gross"] / 100
    )
    assert (
        recurrence_response.operations[0].previous_total_operated_amount_net
        == rru["operations"][0]["previous_total_operated_amount_net"] / 100
    )
    assert recurrence_response.operations[0].ur_amount == rru["operations"][0]["ur_amount"] / 100
    assert (
        recurrence_response.operations[0].operated_amount_gross == rru["operations"][0]["operated_amount_gross"] / 100
    )
    assert recurrence_response.operations[0].operated_amount_net == rru["operations"][0]["operated_amount_net"] / 100
    assert (
        recurrence_response.operations[0].total_operated_amount_gross
        == rru["operations"][0]["total_operated_amount_gross"] / 100
    )
    assert (
        recurrence_response.operations[0].total_operated_amount_net
        == rru["operations"][0]["total_operated_amount_net"] / 100
    )


def test_get_rru_list_by_ur_id(credential, requests_mock, rru_list_mock, recurrence_mock):
    recurrence_id = recurrence_mock["id"]

    url = get_url(APINamespaces.RECURRENCES) + f"{recurrence_id}/receivable-units"

    requests_mock.get(url, json=rru_list_mock, status_code=200)

    recurrence_response = RecurrenceReceivableUnitList.get_by_recurrence_id(
        credential, recurrence_id=recurrence_id, page=1, page_size=10
    )

    recurrence_response = recurrence_response.rrus[0]
    rru = rru_list_mock["rrus"][0]

    assert recurrence_response.id == rru["id"]
    assert recurrence_response.recurrence_id == rru["recurrence_id"]
    assert recurrence_response.ur_id == rru["ur_id"]
    assert recurrence_response.asset_holder == rru["asset_holder"]
    assert recurrence_response.msc_integrator == rru["asset_holder"]
    assert recurrence_response.msc_customer == rru["asset_holder"]
    assert recurrence_response.acquirer == rru["acquirer"]
    assert recurrence_response.payment_scheme == rru["payment_scheme"]
    assert recurrence_response.due_date == datetime.fromisoformat(rru["due_date"])
    assert recurrence_response.amount == rru["amount"] / 100
    assert recurrence_response.total_operated_amount_gross == rru["total_operated_amount_gross"] / 100
    assert recurrence_response.total_operated_amount_net == rru["total_operated_amount_net"] / 100
    assert recurrence_response.available_amount == rru["available_amount"] / 100
    assert recurrence_response.created_at == datetime.fromisoformat(rru["created_at"])
    assert recurrence_response.previous_amount == rru["previous_amount"] / 100
    assert recurrence_response.previous_operated_amount_gross == rru["previous_operated_amount_gross"] / 100
    assert recurrence_response.previous_operated_amount_net == rru["previous_operated_amount_net"] / 100

    assert recurrence_response.operations[0].operation_id == rru["operations"][0]["operation_id"]
    assert recurrence_response.operations[0].operation_date == datetime.fromisoformat(
        rru["operations"][0]["operation_date"]
    )
    assert recurrence_response.operations[0].previous_ur_amount == rru["operations"][0]["previous_ur_amount"] / 100
    assert (
        recurrence_response.operations[0].previous_total_operated_amount_gross
        == rru["operations"][0]["previous_total_operated_amount_gross"] / 100
    )
    assert (
        recurrence_response.operations[0].previous_total_operated_amount_net
        == rru["operations"][0]["previous_total_operated_amount_net"] / 100
    )
    assert recurrence_response.operations[0].ur_amount == rru["operations"][0]["ur_amount"] / 100
    assert (
        recurrence_response.operations[0].operated_amount_gross == rru["operations"][0]["operated_amount_gross"] / 100
    )
    assert recurrence_response.operations[0].operated_amount_net == rru["operations"][0]["operated_amount_net"] / 100
    assert (
        recurrence_response.operations[0].total_operated_amount_gross
        == rru["operations"][0]["total_operated_amount_gross"] / 100
    )
    assert (
        recurrence_response.operations[0].total_operated_amount_net
        == rru["operations"][0]["total_operated_amount_net"] / 100
    )
