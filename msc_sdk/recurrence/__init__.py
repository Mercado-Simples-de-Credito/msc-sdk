# MOCK
import os
import random
import uuid
from datetime import datetime, timedelta

from msc_sdk.commons import BankAccount
from msc_sdk.enums import AccountType


def date_str(delta_days: int) -> str:
    return (datetime.now() + timedelta(days=delta_days)).strftime("%Y-%m-%d")


_msc_customer = os.getenv("MSC_DOCUMENT")
_asset_holders = ["15365935000149"]
_acquirers = ["01027058000191", "15111975000164"]
_payment_schemes = ["VCC", "MCC", "ECC"]
_bank_account = BankAccount(
    branch="1234",
    account="123456",
    account_digit="1",
    account_type=AccountType.CHECKING_ACCOUNT,
    ispb="60701190",
    document_type="CNPJ",
    document_number="74634410000120",
)
_discount_rate = 0.01

# MOCK URS
_urs_count = 5
_urs_list = []

_delta_months = 1
_delta_days = 2
for _ in range(_urs_count):
    for asset_holder in _asset_holders:
        for acquirer in _acquirers:
            for payment_scheme in _payment_schemes:
                delta_days = _delta_days
                for m in range(_delta_months):
                    _urs_list.append(
                        dict(
                            id=str(uuid.uuid4()),
                            asset_holder=_asset_holders,
                            payment_scheme=payment_scheme,
                            acquirer=acquirer,
                            due_date=datetime.now() + timedelta(days=(m + 1) * 30 - delta_days),
                            amount=round(random.uniform(10.00, 1000.00), 2),
                        )
                    )
                    delta_days -= 1

#  MOCK RECURRENCE
_recurrence_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

_recurrence_list = []
_history = {"updated_data": [], "snapshot": {}}
for asset_holder in _asset_holders:
    for recurrence_id in _recurrence_ids:
        for acquirer in _acquirers:
            _recurrence_list.append(
                dict(
                    id=recurrence_id,
                    asset_holder=asset_holder,
                    payment_scheme=_payment_schemes,
                    msc_customer=_msc_customer,
                    msc_integrator=str(uuid.uuid4()),
                    acquirer=acquirer,
                    bank_account=_bank_account,
                    ur_percentage=100,
                    discount_rate_per_year=12,
                    created_at=datetime.now(),
                    history=_history,
                )
            )

#  MOCK OPERATION
_operation_list = []

for recurrence in _recurrence_list:
    operation_receivable_units = []

    total_amount = 0
    total_discount_amount = 0
    for ur in _urs_list:
        days_to_charge = (ur["due_date"] - datetime.now()).days

        total_amount += ur["amount"]
        total_discount_amount += round(ur["amount"] * (_discount_rate / 30) * days_to_charge, 2)

        operation_receivable_units.append(
            dict(
                ur_id=str(uuid.uuid4()),
                msc_customer=_msc_customer,
                asset_holder=recurrence["asset_holder"],
                payment_scheme=ur["payment_scheme"],
                acquirer=ur["acquirer"],
                due_date=ur["due_date"],
                payment_due_date=ur["due_date"],
                amount=ur["amount"],
                discount_rate_per_year=recurrence["discount_rate_per_year"],
                discount_rate=_discount_rate,
                discount_amount=total_discount_amount,
                amount_due=ur["amount"] - total_discount_amount,
            )
        )

    _operation_list.append(
        dict(
            id=str(uuid.uuid4()),
            operation_date=datetime.now() - timedelta(days=_delta_days),
            recurrence_id=recurrence["id"],
            asset_holder=recurrence["asset_holder"],
            operation_receivable_units=operation_receivable_units,
            amount=total_amount,
            amount_due=total_amount - total_discount_amount,
            amount_paid=0 if _delta_days == 0 else total_amount - total_discount_amount,
            bank_account=_bank_account,
            created_at=datetime.now() - timedelta(days=_delta_days),
        )
    )

#  MOCK RRU
_rru_list = []

for operation in _operation_list:
    for ur in operation["operation_receivable_units"]:
        _operations_resume = [
            dict(
                operation_id=str(uuid.uuid4()),
                operation_date=operation["operation_date"] - timedelta(days=1),
                previous_ur_amount=0,
                previous_total_operated_amount_gross=0,
                previous_total_operated_amount_net=0,
                ur_amount=ur["amount"] - 5,
                operated_amount_gross=ur["amount"] - 5,
                operated_amount_net=ur["amount_due"] - 4.5,
                total_operated_amount_gross=ur["amount"] - 5,
                total_operated_amount_net=ur["amount_due"] - 4.5,
            ),
            dict(
                operation_id=operation["id"],
                operation_date=operation["operation_date"],
                previous_ur_amount=ur["amount"] - 5,
                previous_total_operated_amount_gross=ur["amount"] - 5,
                previous_total_operated_amount_net=ur["amount_due"] - 4.5,
                ur_amount=ur["amount"],
                operated_amount_gross=5,
                operated_amount_net=4.5,
                total_operated_amount_gross=ur["amount"],
                total_operated_amount_net=ur["amount_due"],
            ),
        ]
        _rru_list.append(
            dict(
                id=str(uuid.uuid4()),
                recurrence_id=operation["recurrence_id"],
                ur_id=ur["ur_id"],
                asset_holder=ur["asset_holder"],
                msc_integrator=operation["asset_holder"],
                msc_customer=_msc_customer,
                acquirer=ur["acquirer"],
                payment_scheme=ur["payment_scheme"],
                due_date=ur["due_date"],
                amount=ur["amount"],
                total_operated_amount_gross=ur["amount"],
                total_operated_amount_net=ur["amount_due"],
                available_amount=0,
                created_at=datetime.now() - timedelta(days=_delta_days),
                operations=_operations_resume,
                previous_amount=ur["amount"] - 5,
                previous_operated_amount_gross=ur["amount"] - 5,
                previous_operated_amount_net=ur["amount_due"] - 4.5,
                history=_history,
            )
        )

mock_data = dict(
    msc_customer=_msc_customer,
    asset_holders=_asset_holders,
    recurrence_list=_recurrence_list,
    operation_list=_operation_list,
    rru_list=_rru_list,
)

from .recurrence import RecurrenceList, Recurrence  # noqa
from .rru import RecurrenceReceivableUnitList, RecurrenceReceivableUnit  # noqa
from .operation import OperationList, Operation  # noqa
