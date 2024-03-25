import pytest

from msc_sdk.position.position import (
    RequestPositionURList,
    RequestPositionUR,
    RequestPositionType,
    request_position_report,
)


@pytest.fixture
def test_data():
    request_position_ur_list = RequestPositionURList(
        optin=[
            RequestPositionUR(payment_scheme="VCC", acquirer="1027058000191"),
            RequestPositionUR(payment_scheme="MCC", acquirer="1027058000191"),
            RequestPositionUR(payment_scheme="ECC", acquirer="1027058000191"),
        ]
    )

    return dict(asset_holder="44226946000146", request_position_ur_list=request_position_ur_list)


def test_new_single_with_valid_inputs(credential, test_data):
    positions, errors = request_position_report(
        credential,
        test_data["asset_holder"],
        RequestPositionType.SINGLE,
        test_data["request_position_ur_list"],
    )

    assert positions[0].key is not None
    assert positions[0].asset_holder == test_data["asset_holder"]
    assert positions[0].payment_scheme == test_data["request_position_ur_list"]["optin"][0].payment_scheme
    assert positions[0].acquirer == test_data["request_position_ur_list"]["optin"][0].acquirer
    assert positions[0].update_position_start is not None
    assert positions[0].update_position_end is not None
    assert positions[0].key_optin_tag is not None
    assert positions == []
    assert positions[0].total_ur_amount == 0
    assert positions[0].total_value_available == 0
    assert positions[0].ur_list_last_update is None
    assert positions[0].created_on is not None
    assert positions[0].updated_on is None
