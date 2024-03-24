import pytest

from msc_sdk.authenticate.credential import Credential, CredentialPool
from msc_sdk.commons import BankAccount
from msc_sdk.enums import AccountType


def test_new_with_valid_inputs():
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

    credential = Credential.new(document, bank_account, api_user, api_pass, key)

    assert credential.key == key
    assert credential.api_user.get_secret_value() == api_user
    assert credential.api_pass.get_secret_value() == api_pass


def test_new_with_empty_key():
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
    key = ""

    credential = Credential.new(document, bank_account, api_user, api_pass, key)

    assert credential.key is None
    assert credential.api_user.get_secret_value() == api_user
    assert credential.api_pass.get_secret_value() == api_pass


def test_new_with_wrong_document():
    document = "20299078000100"
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

    with pytest.raises(ValueError):
        Credential.new(document, bank_account, api_user, api_pass, key)


def test_new_with_empty_api_user():
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
    api_user = ""
    api_pass = "test_pass"
    key = "test_key"

    with pytest.raises(ValueError):
        Credential.new(document, bank_account, api_user, api_pass, key)


def test_new_with_empty_api_pass():
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
    api_pass = ""
    key = "test_key"

    with pytest.raises(ValueError):
        Credential.new(document, bank_account, api_user, api_pass, key)


def test_credential_pool_add():
    pool = CredentialPool()
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

    pool.add(document, bank_account, api_user, api_pass, key)

    assert len(pool.pool) == 1
    assert pool.pool[0].key == key
    assert pool.pool[0].api_user.get_secret_value() == api_user
    assert pool.pool[0].api_pass.get_secret_value() == api_pass


def test_credential_pool_get_by_key():
    pool = CredentialPool()
    document1 = "20299078000166"
    bank_account1 = BankAccount(
        branch="1234",
        account="123456789",
        account_digit="1",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="12345678900",
        document_type="CNPJ",
        document_number="20299078000166",
    )
    api_user1 = "user1"
    api_pass1 = "pass1"
    key1 = "key1"

    document2 = "03205714000124"
    bank_account2 = BankAccount(
        branch="1234",
        account="123456789",
        account_digit="1",
        account_type=AccountType.CHECKING_ACCOUNT,
        ispb="12345678900",
        document_type="CNPJ",
        document_number="03205714000124",
    )
    api_user2 = "user2"
    api_pass2 = "pass2"
    key2 = "key2"

    pool.add(document1, bank_account1, api_user1, api_pass1, key1)
    pool.add(document2, bank_account2, api_user2, api_pass2, key2)

    retrieved_credential = pool.get_by_key(key2)

    assert retrieved_credential.key == key2
    assert retrieved_credential.api_user.get_secret_value() == api_user2
    assert retrieved_credential.api_pass.get_secret_value() == api_pass2
