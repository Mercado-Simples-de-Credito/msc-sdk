import os

import pytest

from msc_sdk.authenticate import Credential, Authenticate
from msc_sdk.commons import BankAccount
from msc_sdk.config_sdk import ConfigSDK, Environment
from msc_sdk.enums import AccountType


@pytest.fixture(autouse=True)
def setup_config():
    ConfigSDK.setup(environment=Environment.TEST)


@pytest.fixture
def env_vars() -> dict:
    return dict(
        document=os.getenv("MSC_DOCUMENT"),
        api_user=os.getenv("MSC_API_USER"),
        api_pass=os.getenv("MSC_API_PASS"),
    )


@pytest.fixture
def credential(env_vars) -> Credential:
    document = env_vars["document"]
    bank_account = BankAccount(
        branch="1234",
        account="123456789",
        account_digit="1",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="12345678900",
        document_type="CNPJ",
        document_number=env_vars["document"],
    )
    api_user = env_vars["api_user"]
    api_pass = env_vars["api_pass"]

    return Credential.new(document, bank_account, api_user, api_pass)


@pytest.fixture
def authenticate(credential) -> Authenticate:
    return Authenticate.token(credential)
