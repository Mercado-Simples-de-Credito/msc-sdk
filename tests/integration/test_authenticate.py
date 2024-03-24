from msc_sdk.commons import BankAccount, AccountType
from msc_sdk.authenticate import Authenticate
from msc_sdk.authenticate.credential import Credential


def test_authenticate_token_success(env_vars):
    credential = Credential.new(
        env_vars["document"],
        BankAccount(
            branch="1234",
            account="123456789",
            account_digit="1",
            account_type=AccountType.CHECKING_ACCOUNT,
            ispb="12345678900",
            document_type="CNPJ",
            document_number=env_vars["document"],
        ),
        env_vars["api_user"],
        env_vars["api_pass"],
    )

    authenticate = Authenticate.token(credential)

    assert authenticate.access_token.get_secret_value() is not None
