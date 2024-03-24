from typing import Self, List

from pydantic import BaseModel, SecretStr, model_validator

from msc_sdk.commons import BankAccount
from msc_sdk.utils.validators import validate_cnpj


class Credential(BaseModel):
    """
    Credential of an API user that can be used to authenticate.
    """

    key: str = None
    document: str
    bank_account: BankAccount
    api_user: SecretStr
    api_pass: SecretStr

    class Config:
        validate_assignment = True

    @model_validator(mode="before")
    def validate(self):
        if self.get("document", None):
            self["document"] = validate_cnpj(self["document"])

        return self

    @classmethod
    def new(
        cls,
        document: str,
        bank_account: BankAccount,
        api_user: str,
        api_pass: str,
        key: str = None,
    ) -> Self:
        """
        Create a new credential object.

        Args:
            document (str): The document (CNPJ) of the user.
            bank_account (BankAccount): The bank account of the user.
            api_user (str): The API user.
            api_pass (str): The API password.
            key (str, optional): The key used to identify the credential. Defaults to None.

        Returns:
            Credential: A new credential object.
        """
        if not api_user:
            raise ValueError("api_user cannot be empty")

        if not api_pass:
            raise ValueError("api_pass cannot be empty")

        data = dict(
            document=document,
            bank_account=bank_account,
            api_user=SecretStr(api_user),
            api_pass=SecretStr(api_pass),
        )

        if key:
            data["key"] = key

        credential = cls(**data)
        return credential


class CredentialPool(BaseModel):
    """
    Pool of credentials that can be used to authenticate.
    """

    pool: List[Credential] = []

    class Config:
        validate_assignment = True

    def add(
        self,
        document: str,
        bank_account: BankAccount,
        api_user: str,
        api_pass: str,
        key: str,
    ):
        """
        Adds a new credential to the pool.

        Parameters:
            document (str): The document (CNPJ) of the user.
            bank_account (BankAccount): The bank account of the user.
            api_user (str): The API user of the credential.
            api_pass (str): The API password of the credential.
            key (str): The key of the credential.

        Returns:
            None
        """
        credential = Credential.new(
            document=document,
            bank_account=bank_account,
            api_user=api_user,
            api_pass=api_pass,
            key=key,
        )
        self.pool.append(credential)

    def get_by_key(self, key: str) -> Credential:
        """
        A function that retrieves a credential from the pool by key.

        Args:
            key (str): The key of the credential to retrieve.

        Returns:
            Credential: The retrieved credential.
        """
        for credential in self.pool:
            if credential.key == key:
                return credential
