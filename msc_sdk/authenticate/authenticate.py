from typing import Self

import requests
from pydantic import BaseModel, SecretStr
import cachetools

from msc_sdk.authenticate.credential import Credential
from msc_sdk.enums import APINamespaces
from msc_sdk.errors import Unauthorized, ServerError, NotFound
from msc_sdk.utils.api_tools import get_url


class Authenticate(BaseModel):
    """
    An authentication object, which contains the token to access the MSC API.
    """

    access_token: SecretStr = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    @classmethod
    def token(cls, credential: Credential) -> Self:
        """
        Args:
            credential (Credential): The credential object containing the API user and password.

        Returns:
            Authenticate: An instance of the class with an access token if the response status code is 200.

        Raises:
            Unauthorized: If the response status code is 401.
            ServerError: If the response status code is 500 or above.
            Exception: If the response status code is none of the above.
        """
        api_path = "token"

        response_data = _token_request(
            get_url(APINamespaces.AUTHENTICATE, api_path),
            credential.api_user,
            credential.api_pass,
        )

        return cls(access_token=SecretStr(response_data["access_token"]))


@cachetools.cached(cache=cachetools.TTLCache(maxsize=100, ttl=6000))
def _token_request(url: str, api_user: SecretStr, api_pass: SecretStr) -> dict:
    """
    A function that sends a token request to the given URL and returns the response.

    Args:
        url (str): The URL to which the token request is sent.
        credential (Credential): The credential object containing the API user and password.

    Returns:
        requests.Response: The response from the token request.
    """
    response = requests.post(url=url, auth=(api_user.get_secret_value(), api_pass.get_secret_value()))

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 401:
        raise Unauthorized("Wrong credentials")

    elif response.status_code >= 500:
        raise ServerError("Server error")

    raise Exception(f"Unexpected error - status code {response.status_code} - response: {response.text}")
