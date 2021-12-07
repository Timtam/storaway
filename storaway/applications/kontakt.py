import os.path
import pathlib
import winreg
from typing import Iterator, List, Sequence, cast

from collectors.collector import Collector
from collectors.file_collector import FileCollector
from collectors.registry_collector import RegistryCollector
from utils.platform import Platform
from utils.registry_value import RegistryValue

from .application import Application


class Kontakt(Application):

    name = "Kontakt"
    description = "Native Instruments Kontakt Library Database"
    platforms = (Platform.WINDOWS,)
    _directories: List[pathlib.Path] = []

    def prepare_collectors(self) -> Iterator[Collector]:
        yield self.get_collector(
            RegistryCollector,
            "software",
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            self.detect_kontakt_library,
        )

        for dir in self._directories:
            yield self.get_collector(FileCollector, str(dir), dir)

    def detect_kontakt_library(
        self, values: Sequence[RegistryValue]
    ) -> Sequence[RegistryValue]:

        is_kontakt_library: bool = False

        for value in values:
            if (
                value.name == "URLUpdateInfo"
                and value.value == "http://www.native-instruments.de/"
            ):
                is_kontakt_library = True
                break

        if is_kontakt_library:

            for value in values:
                if value.name == "DisplayIcon" and os.path.exists(
                    os.path.dirname(cast(str, value.value))
                ):
                    self._directories.append(
                        pathlib.Path(os.path.dirname(cast(str, value.value)))
                    )
                    break

            return values

        return []
