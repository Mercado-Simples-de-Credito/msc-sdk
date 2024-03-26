# MOCK
import random
import uuid
from datetime import datetime, timedelta

from msc_sdk.commons import BankAccount
from msc_sdk.enums import AccountType


def date_str(delta_days: int) -> str:
    return (datetime.now() + timedelta(days=delta_days)).strftime("%Y-%m-%d")


_asset_holders = ["15365935000149"]
_acquirers = ["1027058000191"]
_payment_schemes = ["VCC", "MCC", "ECC"]
_bank_account = BankAccount(
    branch="1234",
    account="123456",
    account_digit="1",
    account_type=AccountType.CHECKING_ACCOUNT,
    ispb="12345678900",
    document_type="CNPJ",
    document_number="74634410000120",
)


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
for asset_holder in _asset_holders:
    for recurrence_id in _recurrence_ids:
        for acquirer in _acquirers:
            _recurrence_list.append(
                dict(
                    id=recurrence_id,
                    asset_holder=asset_holder,
                    payment_scheme=_payment_schemes,
                    acquirer=acquirer,
                    bank_account=_bank_account,
                    discount_rate_per_year=12,
                    created_at=datetime.now(),
                )
            )


#  MOCK OPERATION
_operation_list = []

for recurrence in _recurrence_list:
    operation_receivable_units = []

    total_amount = 0
    total_discount_amount = 0
    for ur in _urs_list:
        discount_rate = (ur["due_date"] - datetime.now()).days

        total_amount += ur["amount"]
        total_discount_amount += round(ur["amount"] * discount_rate / 100, 2)

        operation_receivable_units.append(
            dict(
                ur_id=str(uuid.uuid4()),
                asset_holder=recurrence["asset_holder"],
                payment_scheme=ur["payment_scheme"],
                acquirer=ur["acquirer"],
                due_date=ur["due_date"],
                payment_due_date=ur["due_date"],
                amount=ur["amount"],
                discount_rate_per_year=recurrence["discount_rate_per_year"],
                discount_rate=discount_rate,
                discount_amount=round(ur["amount"] * discount_rate / 100, 2),
                amount_due=round(ur["amount"] - round(ur["amount"] * discount_rate / 100, 2), 2),
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
        _rru_list.append(
            dict(
                id=str(uuid.uuid4()),
                recurrence_id=operation["recurrence_id"],
                ur_id=ur["ur_id"],
                asset_holder=ur["asset_holder"],
                acquirer=ur["acquirer"],
                payment_scheme=ur["payment_scheme"],
                due_date=ur["due_date"],
                amount=ur["amount"],
                operated_amount_gross=ur["amount"],
                operated_amount_net=ur["amount_due"],
                available_amount=0,
                created_at=datetime.now() - timedelta(days=_delta_days),
            )
        )


mock_data = dict(
    asset_holders=_asset_holders,
    recurrence_list=_recurrence_list,
    operation_list=_operation_list,
    rru_list=_rru_list,
)


from .recurrence import RecurrenceList, Recurrence  # noqa
from .rru import RecurrenceReceivableUnitList, RecurrenceReceivableUnit  # noqa
from .operation import OperationList, Operation  # noqa
