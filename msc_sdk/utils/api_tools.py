from msc_sdk.enums import APINamespaces
from msc_sdk.config_sdk import ConfigSDK


def get_url(namespace: APINamespaces, api_path: str = None) -> str:
    """
    Concatenates the base URL from the Config class with the provided namespace and API path
    and returns the resulting URL.

    Args:
        namespace (str): The namespace for the URL.
        api_path (str): The API path for the URL.

    Returns:
        str: The constructed URL.
    """
    if not api_path:
        url = f"{ConfigSDK.get_config().base_url}{namespace.value}/"
    else:
        url = f"{ConfigSDK.get_config().base_url}{namespace.value}/{api_path}"

    return url
