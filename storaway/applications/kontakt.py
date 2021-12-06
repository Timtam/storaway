import winreg
from typing import Sequence

from collectors.registry_collector import RegistryCollector
from utils.platform import Platform
from utils.registry_value import RegistryValue

from .application import Application


class Kontakt(Application):

    name = "Kontakt"
    description = "Native Instruments Kontakt Library Database"
    platforms = (Platform.WINDOWS,)

    def prepare_collectors(self) -> Sequence[RegistryCollector]:
        return [
            self.get_collector(
                RegistryCollector,
                "software",
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                self.detect_kontakt_library,
            ),
        ]

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
            return values

        return []
