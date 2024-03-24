import pytest

from msc_sdk.enums import APINamespaces
from msc_sdk.commons import BankAccount, AccountType
from msc_sdk.utils.api_tools import get_url
from msc_sdk.authenticate import Authenticate
from msc_sdk.authenticate.credential import Credential
from msc_sdk.errors import Unauthorized, ServerError


def test_authenticate_token_unauthorized(requests_mock):
    credential = Credential.new(
        "20299078000166",
        BankAccount(
            branch="1234",
            account="123456789",
            account_digit="1",
            account_type=AccountType.CHECKING_ACCOUNT,
            ispb="12345678900",
            document_type="CNPJ",
            document_number="20299078000166",
        ),
        "test_key",
        "test_user",
        "test_pass",
    )

    requests_mock.post(get_url(APINamespaces.AUTHENTICATE, "token"), status_code=401)

    with pytest.raises(Unauthorized):
        Authenticate.token(credential)


def test_authenticate_token_server_error(requests_mock):
    credential = Credential.new(
        "20299078000166",
        BankAccount(
            branch="1234",
            account="123456789",
            account_digit="1",
            account_type=AccountType.CHECKING_ACCOUNT,
            ispb="12345678900",
            document_type="CNPJ",
            document_number="20299078000166",
        ),
        "test_key",
        "test_user",
        "test_pass",
    )

    requests_mock.post(get_url(APINamespaces.AUTHENTICATE, "token"), status_code=500)

    with pytest.raises(ServerError):
        Authenticate.token(credential)


def test_authenticate_token_unexpected_error(requests_mock):
    credential = Credential.new(
        "20299078000166",
        BankAccount(
            branch="1234",
            account="123456789",
            account_digit="1",
            account_type=AccountType.CHECKING_ACCOUNT,
            ispb="12345678900",
            document_type="CNPJ",
            document_number="20299078000166",
        ),
        "test_key",
        "test_user",
        "test_pass",
    )

    requests_mock.post(get_url(APINamespaces.AUTHENTICATE, "token"), status_code=404)

    with pytest.raises(Exception):
        Authenticate.token(credential)


def test_authenticate_token_success(requests_mock):
    credential = Credential.new(
        "20299078000166",
        BankAccount(
            branch="1234",
            account="123456789",
            account_digit="1",
            account_type=AccountType.CHECKING_ACCOUNT,
            ispb="12345678900",
            document_type="CNPJ",
            document_number="20299078000166",
        ),
        "test_key",
        "test_user",
        "test_pass",
    )

    access_token = "test_token"
    response_data = {"access_token": access_token}
    requests_mock.post(
        get_url(APINamespaces.AUTHENTICATE, "token"),
        json=response_data,
        status_code=200,
    )

    authenticate = Authenticate.token(credential)

    assert authenticate.access_token.get_secret_value() == access_token
