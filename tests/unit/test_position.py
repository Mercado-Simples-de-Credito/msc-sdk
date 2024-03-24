import uuid
from datetime import datetime

import pytest

from msc_sdk.enums import APINamespaces
from msc_sdk.position.position import (
    RequestPositionURList,
    RequestPositionUR,
    RequestPositionType,
    request_position_report,
    Position,
)
from msc_sdk.utils.api_tools import get_url


@pytest.fixture
def test_data():
    request_position_ur_list = RequestPositionURList(
        optin=[
            RequestPositionUR(payment_scheme="VCC", acquirer="41548447000187"),
            RequestPositionUR(payment_scheme="MCC", acquirer="41548447000187"),
            RequestPositionUR(payment_scheme="ECC", acquirer="41548447000187"),
        ]
    )

    asset_holder = "44226946000146"
    update_position_start = datetime.now().isoformat()

    positions = []
    for ur in request_position_ur_list.optin:
        positions.append(
            dict(
                key=str(uuid.uuid4()),
                asset_holder=asset_holder,
                payment_scheme=ur.payment_scheme,
                acquirer=ur.acquirer,
                update_position_start=update_position_start,
                update_position_end=update_position_start,
                key_optin_tag=str(uuid.uuid4()),
                ur_list_resume=[
                    dict(due_date="2030-01-01", ur_amount=1000, value_available=1000),
                    dict(due_date="2030-02-01", ur_amount=2000, value_available=2000),
                    dict(due_date="2030-03-01", ur_amount=3000, value_available=3000),
                ],
                total_ur_amount=6000,
                total_value_available=6000,
                ur_list_last_update=datetime.now().isoformat(),
                created_on=datetime.now().isoformat(),
                updated_on=datetime.now().isoformat(),
            )
        )

    return dict(asset_holder="44226946000146", request_position_ur_list=request_position_ur_list, positions=positions)


def test_new_single_with_valid_inputs(credential, test_data, requests_mock):
    post_response_data = dict(optin=[])

    for position in test_data["positions"]:
        post_response_data["optin"].append(
            dict(payment_scheme=position["payment_scheme"], acquirer=position["acquirer"], success=True)
        )
        # fmt: off
        get_parms_data = (f"?payment_scheme={position['payment_scheme']}&acquirer={position['acquirer']}"
                          f"&asset_holder={test_data['asset_holder']}&msc_customer={credential.document}")
        # fmt: on
        url = get_url(APINamespaces.POSITIONS, "report") + get_parms_data

        requests_mock.get(url, json=position, status_code=200)

    requests_mock.post(get_url(APINamespaces.POSITIONS, "report"), json=post_response_data, status_code=200)

    positions, errors = request_position_report(
        credential, test_data["asset_holder"], RequestPositionType.SINGLE, test_data["request_position_ur_list"]
    )

    assert positions[0].key == test_data["positions"][0]["key"]
    assert positions[0].asset_holder == test_data["positions"][0]["asset_holder"]
    assert positions[0].payment_scheme == test_data["positions"][0]["payment_scheme"]
    assert positions[0].acquirer == test_data["positions"][0]["acquirer"]
    assert positions[0].update_position_start.isoformat() == test_data["positions"][0]["update_position_start"]
    assert positions[0].update_position_end.isoformat() == test_data["positions"][0]["update_position_end"]
    assert positions[0].key_optin_tag == test_data["positions"][0]["key_optin_tag"]

    assert (
        positions[0].ur_list_resume[0].due_date.strftime("%Y-%m-%d")
        == test_data["positions"][0]["ur_list_resume"][0]["due_date"]
    )
    assert positions[0].ur_list_resume[0].ur_amount == test_data["positions"][0]["ur_list_resume"][0]["ur_amount"] / 100
    assert (
        positions[0].ur_list_resume[0].value_available
        == test_data["positions"][0]["ur_list_resume"][0]["value_available"] / 100
    )
    assert (
        positions[0].ur_list_resume[1].due_date.strftime("%Y-%m-%d")
        == test_data["positions"][0]["ur_list_resume"][1]["due_date"]
    )
    assert positions[0].ur_list_resume[1].ur_amount == test_data["positions"][0]["ur_list_resume"][1]["ur_amount"] / 100
    assert (
        positions[0].ur_list_resume[1].value_available
        == test_data["positions"][0]["ur_list_resume"][1]["value_available"] / 100
    )

    assert (
        positions[1].ur_list_resume[0].due_date.strftime("%Y-%m-%d")
        == test_data["positions"][1]["ur_list_resume"][0]["due_date"]
    )
    assert positions[1].ur_list_resume[0].ur_amount == test_data["positions"][1]["ur_list_resume"][0]["ur_amount"] / 100
    assert (
        positions[1].ur_list_resume[0].value_available
        == test_data["positions"][1]["ur_list_resume"][0]["value_available"] / 100
    )
    assert (
        positions[1].ur_list_resume[1].due_date.strftime("%Y-%m-%d")
        == test_data["positions"][1]["ur_list_resume"][1]["due_date"]
    )
    assert positions[1].ur_list_resume[1].ur_amount == test_data["positions"][1]["ur_list_resume"][1]["ur_amount"] / 100
    assert (
        positions[1].ur_list_resume[1].value_available
        == test_data["positions"][1]["ur_list_resume"][1]["value_available"] / 100
    )

    assert positions[0].total_ur_amount == test_data["positions"][0]["total_ur_amount"] / 100
    assert positions[0].total_value_available == test_data["positions"][0]["total_value_available"] / 100
    assert positions[0].ur_list_last_update.isoformat() == test_data["positions"][0]["ur_list_last_update"]
    assert positions[0].created_on.isoformat() == test_data["positions"][0]["created_on"]
    assert positions[0].updated_on.isoformat() == test_data["positions"][0]["updated_on"]


def test_get_with_valid_inputs(credential, test_data, requests_mock):
    # fmt: off
    get_parms_data = (f'?payment_scheme={test_data["positions"][0]["payment_scheme"]}'
                      f'&acquirer={test_data["positions"][0]["acquirer"]}&asset_holder={test_data["asset_holder"]}'
                      f'&msc_customer={credential.document}')
    # fmt: on
    url = get_url(APINamespaces.POSITIONS, "report") + get_parms_data

    requests_mock.get(url, json=test_data["positions"][0], status_code=200)

    position = Position.get_by_data(
        credential,
        test_data["positions"][0]["payment_scheme"],
        acquirer=test_data["positions"][0]["acquirer"],
        asset_holder=test_data["asset_holder"],
    )

    assert position.key == test_data["positions"][0]["key"]
    assert position.asset_holder == test_data["positions"][0]["asset_holder"]
    assert position.payment_scheme == test_data["positions"][0]["payment_scheme"]
    assert position.acquirer == test_data["positions"][0]["acquirer"]
    assert position.update_position_start.isoformat() == test_data["positions"][0]["update_position_start"]
    assert position.update_position_end.isoformat() == test_data["positions"][0]["update_position_end"]
    assert position.key_optin_tag == test_data["positions"][0]["key_optin_tag"]
    assert (
        position.ur_list_resume[0].due_date.strftime("%Y-%m-%d")
        == test_data["positions"][0]["ur_list_resume"][0]["due_date"]
    )
    assert position.ur_list_resume[0].ur_amount == test_data["positions"][0]["ur_list_resume"][0]["ur_amount"] / 100
    assert (
        position.ur_list_resume[0].value_available
        == test_data["positions"][0]["ur_list_resume"][0]["value_available"] / 100
    )
    assert (
        position.ur_list_resume[1].due_date.strftime("%Y-%m-%d")
        == test_data["positions"][0]["ur_list_resume"][1]["due_date"]
    )
    assert position.ur_list_resume[1].ur_amount == test_data["positions"][0]["ur_list_resume"][1]["ur_amount"] / 100
    assert (
        position.ur_list_resume[1].value_available
        == test_data["positions"][0]["ur_list_resume"][1]["value_available"] / 100
    )
    assert position.total_ur_amount == test_data["positions"][0]["total_ur_amount"] / 100
    assert position.total_value_available == test_data["positions"][0]["total_value_available"] / 100
    assert position.ur_list_last_update.isoformat() == test_data["positions"][0]["ur_list_last_update"]
    assert position.created_on.isoformat() == test_data["positions"][0]["created_on"]
    assert position.updated_on.isoformat() == test_data["positions"][0]["updated_on"]
