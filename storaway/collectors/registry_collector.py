import pickle
import winreg
from typing import IO, Callable, List, Optional, Sequence

from utils.registry_value import RegistryValue

from .collector import Collector


class RegistryCollector(Collector):

    key: int
    sub_key: str
    filter: Optional[Callable[[Sequence[RegistryValue]], Sequence[RegistryValue]]]
    access: int

    def __init__(
        self,
        key: int,
        sub_key: str,
        access: int = 0,
        filter: Optional[
            Callable[[Sequence[RegistryValue]], Sequence[RegistryValue]]
        ] = None,
    ) -> None:
        super().__init__()

        self.key = key
        self.sub_key = sub_key
        self.filter = filter
        self.access = access

    def collect(self, output: IO[bytes]) -> None:

        values: List[RegistryValue] = []

        def aggregate_values(
            registry: winreg.HKEYType,
            sub_key: str,
            filter: Optional[
                Callable[[Sequence[RegistryValue]], Sequence[RegistryValue]]
            ],
            access: int,
        ) -> None:

            nonlocal values

            key_values: List[RegistryValue] = []
            key_obj = winreg.OpenKey(key=registry, sub_key=sub_key, access=access)

            key_info = winreg.QueryInfoKey(key_obj)

            for index in range(key_info[1]):

                value_info = winreg.EnumValue(key_obj, index)

                value = RegistryValue()

                value.sub_key = sub_key[len(self.sub_key) + 1 :]
                value.name = value_info[0]
                value.value = value_info[1]
                value.type = value_info[2]

                key_values.append(value)

            if filter:
                key_values = list(filter(key_values))

            if len(key_values) > 0:
                values = values + key_values

            for index in range(key_info[0]):

                sub_key_name = winreg.EnumKey(key_obj, index)

                aggregate_values(
                    registry=registry,
                    sub_key=sub_key + "\\" + sub_key_name,
                    filter=filter,
                    access=access,
                )

            key_obj.Close()

        self.application.echo("Searching for registry values...")

        registry = winreg.ConnectRegistry(None, self.key)

        aggregate_values(
            registry=registry,
            sub_key=self.sub_key,
            filter=self.filter,
            access=winreg.KEY_READ | self.access,
        )

        registry.Close()

        self.application.echo(f"Found {len(values)} values.")

        output.write(pickle.dumps(values))
