import pickle
import winreg
from typing import IO, Callable, List, Optional, Sequence

from utils.registry_value import RegistryValue

from .collector import Collector


class RegistryCollector(Collector):

    key: int
    sub_key: str
    filter: Optional[Callable[[Sequence[RegistryValue]], Sequence[RegistryValue]]]

    def __init__(
        self,
        key: int,
        sub_key: str,
        filter: Optional[
            Callable[[Sequence[RegistryValue]], Sequence[RegistryValue]]
        ] = None,
    ) -> None:
        super().__init__()

        self.key = key
        self.sub_key = sub_key
        self.filter = filter

    def collect(self, output: IO[bytes]) -> None:

        values: List[RegistryValue] = []

        def aggregate_values(
            key: int,
            sub_key: str,
            filter: Optional[
                Callable[[Sequence[RegistryValue]], Sequence[RegistryValue]]
            ],
        ) -> None:

            nonlocal values

            key_values: List[RegistryValue] = []
            key_obj = winreg.OpenKey(key=key, sub_key=sub_key)

            key_info = winreg.QueryInfoKey(key_obj)

            for index in range(key_info[1]):

                value_info = winreg.EnumValue(key_obj, index)

                value = RegistryValue()

                value.key = key
                value.sub_key = sub_key
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
                    key=key, sub_key=sub_key + "\\" + sub_key_name, filter=filter
                )

            key_obj.Close()

        self.application.echo("Searching for registry values...")

        aggregate_values(key=self.key, sub_key=self.sub_key, filter=self.filter)

        self.application.echo(f"Found {len(values)} values.")

        output.write(pickle.dumps(values))
