import os.path
import pathlib
import winreg
from typing import Iterator, List, Sequence, cast

from collectors.collector import Collector
from collectors.file_collector import FileCollector
from collectors.registry_collector import RegistryCollector
from utils.platform import Platform, is_64bit
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
            "uninstall_32bit",
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            winreg.KEY_WOW64_32KEY,
            self.detect_kontakt_uninstaller,
        )

        yield self.get_collector(
            RegistryCollector,
            "kontakt_machine_32bit",
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Native Instruments",
            winreg.KEY_WOW64_32KEY,
            self.detect_kontakt_library,
        )

        yield self.get_collector(
            RegistryCollector,
            "kontakt_user_32bit",
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Native Instruments",
            winreg.KEY_WOW64_32KEY,
        )

        if is_64bit():

            yield self.get_collector(
                RegistryCollector,
                "kontakt_machine_64bit",
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Native Instruments",
                winreg.KEY_WOW64_64KEY,
                self.detect_kontakt_library,
            )

            yield self.get_collector(
                RegistryCollector,
                "kontakt_user_64bit",
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Native Instruments",
                winreg.KEY_WOW64_64KEY,
            )

        for dir in self._directories:
            yield self.get_collector(FileCollector, str(dir), dir)

    def detect_kontakt_uninstaller(
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

    def detect_kontakt_library(
        self, values: Sequence[RegistryValue]
    ) -> Sequence[RegistryValue]:

        is_kontakt_library: bool = False

        for value in values:

            if (
                value.name == "ContentDir"
                and os.path.exists(cast(str, value.value))
                and sum(1 for _ in pathlib.Path(cast(str, value.value)).glob("*.nicnt"))
                >= 1
            ):
                is_kontakt_library = True

        if is_kontakt_library:
            return values

        return []
