from msc_sdk.authenticate.credential import Credential
from msc_sdk.commons import BankAccount
from msc_sdk.enums import AccountType


def test_new_with_valid_inputs(env_vars):
    bank_account = BankAccount(
        branch="1234",
        account="123456789",
        account_digit="1",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="12345678900",
        document_type="CNPJ",
        document_number=env_vars["document"],
    )

    credential = Credential.new(env_vars["document"], bank_account, env_vars["api_user"], env_vars["api_pass"])

    assert credential.api_user.get_secret_value() == env_vars["api_user"]
    assert credential.api_pass.get_secret_value() == env_vars["api_pass"]
