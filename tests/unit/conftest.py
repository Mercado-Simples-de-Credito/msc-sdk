import pytest

from msc_sdk.authenticate import Credential
from msc_sdk.commons import BankAccount
from msc_sdk.config_sdk import ConfigSDK, Environment
from msc_sdk.enums import AccountType, APINamespaces
from msc_sdk.utils.api_tools import get_url


@pytest.fixture(autouse=True)
def setup_config():
    ConfigSDK.setup(environment=Environment.TEST)


@pytest.fixture
def credential(requests_mock) -> Credential:
    document = "20299078000166"
    bank_account = BankAccount(
        branch="1234",
        account="123456789",
        account_digit="1",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="12345678900",
        document_type="CNPJ",
        document_number="20299078000166",
    )
    api_user = "test_user"
    api_pass = "test_pass"
    key = "test_key"

    access_token = "test_token"
    response_data = {"access_token": access_token}
    requests_mock.post(
        get_url(APINamespaces.AUTHENTICATE, "token"),
        json=response_data,
        status_code=200,
    )

    return Credential.new(document, bank_account, api_user, api_pass, key)
