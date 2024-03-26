from msc_sdk.recurrence import mock_data
from msc_sdk.recurrence import Operation, OperationList
from msc_sdk.recurrence import RecurrenceList, Recurrence
from msc_sdk.recurrence import RecurrenceReceivableUnitList, RecurrenceReceivableUnit


def test_get_recurrence_list_with_valid_inputs(credential):
    recurrence_list = RecurrenceList.get(credential, 1, 1000)

    assert len(recurrence_list.recurrences) > 0


def test_get_recurrence_with_valid_inputs(credential):
    recurrence_list = RecurrenceList.get(credential, 1, 1000)

    recurrence = Recurrence.get_by_id(credential, recurrence_list.recurrences[0].id)

    assert recurrence.id == recurrence_list.recurrences[0].id


def test_get_operation_list_with_valid_inputs(credential):
    operation_list = OperationList.get(credential, 1, 1000)

    assert len(operation_list.operations) > 0


def test_get_operation_with_valid_inputs(credential):
    operation_list = OperationList.get(credential, 1, 1000)

    operation = Operation.get_by_id(credential, operation_list.operations[0].id)

    assert operation.id == operation_list.operations[0].id


def test_get_rru_list_with_valid_inputs(credential):
    rru_list = RecurrenceReceivableUnitList.get_by_recurrence_id(
        credential, mock_data["rru_list"][0]["recurrence_id"], 1, 1000
    )

    assert len(rru_list.rrus) > 0


def test_get_rru_with_valid_inputs(credential):
    rru_list = RecurrenceReceivableUnitList.get_by_recurrence_id(
        credential, mock_data["rru_list"][0]["recurrence_id"], 1, 1000
    )

    rru = RecurrenceReceivableUnit.get_by_ur_id(credential, rru_list.rrus[0].ur_id)

    assert rru.id == rru_list.rrus[0].id
