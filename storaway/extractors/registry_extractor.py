import pickle
import winreg
from typing import List

from utils.registry_value import RegistryValue

from .extractor import Extractor


class RegistryExtractor(Extractor):

    key: int
    sub_key: str
    access: int

    def __init__(self, key: int, sub_key: str, access: int = 0) -> None:
        super().__init__()

        self.key = key
        self.sub_key = sub_key
        self.access = access

    def extract(self) -> None:

        self.application.echo("Searching for registry values...")

        values: List[RegistryValue] = pickle.loads(self.input.read())

        self.application.echo(f"Found {len(values)} files.")

        registry = winreg.ConnectRegistry(None, self.key)

        for value in values:

            key = winreg.CreateKeyEx(
                key=registry,
                sub_key=self.sub_key + "\\" + value.sub_key,
                access=winreg.KEY_WRITE | self.access,
            )

            winreg.SetValueEx(
                key,
                value.name,
                0,
                value.type,
                value.value,
            )

            key.Close()

        registry.Close()
