from enum import Enum
from typing import Self, Annotated

from pydantic import BaseModel, model_validator, UrlConstraints
from pydantic_core import Url


class Environment(str, Enum):
    TEST = "test"
    PRODUCTION = "production"

    def __str__(self):
        return self.value


class ConfigSDK(BaseModel):
    environment: Environment
    base_url: Annotated[
        Url,
        UrlConstraints(max_length=2083, allowed_schemes=["https"], host_required=True),
    ] = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    @model_validator(mode="before")
    def validate(self):
        if not self.get("base_url", None):
            if self.get("environment") == Environment.PRODUCTION:
                self["base_url"] = "https://backend.mercadosimples.tech"
            else:
                self["base_url"] = "https://backend-test.mercadosimples.tech"

        return self

    @classmethod
    def setup(cls, environment: Environment) -> Self:
        if not hasattr(cls, "_instance"):
            cls._instance = cls(environment=environment)
            return cls._instance
        return cls._instance

    @classmethod
    def get_config(cls) -> Self:
        if not hasattr(cls, "_instance"):
            raise Exception("Config is not setup")
        return cls._instance
