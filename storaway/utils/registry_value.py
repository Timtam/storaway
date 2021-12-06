from dataclasses import dataclass
from typing import Union


@dataclass(init=False)
class RegistryValue:
    key: int
    sub_key: str
    type: int
    name: str
    value: Union[str, int]
