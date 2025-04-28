from enum import Enum
from typing import Any
from chimera_conf import ChimeraConf
from pydantic import BaseModel, Field


class ConcreteImplementationConfig(BaseModel):
    class_: str | None = Field(None, alias="class")
    depends_on: dict[str, str] = Field(default_factory=dict)
    class_kwargs: dict[str, Any] = Field(default_factory=dict)


class IndividualServiceConfig(BaseModel):
    use: str
    implementations: dict[str, ConcreteImplementationConfig]


class GrimoireConfig(ChimeraConf):
    _config_files = None
    runes: dict[str, IndividualServiceConfig] | None = None


class RuneKey(str, Enum):
    pass
