import os.path
import pathlib
import winreg
from typing import IO, Dict, Iterator, List, Sequence, cast

from collectors.collector import Collector
from collectors.file_collector import FileCollector
from collectors.registry_collector import RegistryCollector
from extractors.extractor import Extractor
from extractors.file_extractor import FileExtractor
from extractors.registry_extractor import RegistryExtractor
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

    def prepare_extractors(self, files: Dict[str, IO[bytes]]) -> Iterator[Extractor]:

        yield self.get_extractor(
            RegistryExtractor,
            files["uninstall_32bit"],
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            winreg.KEY_WOW64_32KEY,
        )

        yield self.get_extractor(
            RegistryExtractor,
            files["kontakt_machine_32bit"],
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Native Instruments",
            winreg.KEY_WOW64_32KEY,
        )

        yield self.get_extractor(
            RegistryExtractor,
            files["kontakt_user_32bit"],
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Native Instruments",
            winreg.KEY_WOW64_32KEY,
        )

        if is_64bit():

            try:

                yield self.get_extractor(
                    RegistryExtractor,
                    files["kontakt_machine_64bit"],
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Native Instruments",
                    winreg.KEY_WOW64_64KEY,
                )

            except KeyError:
                pass

            try:

                yield self.get_extractor(
                    RegistryExtractor,
                    files["kontakt_user_64bit"],
                    winreg.HKEY_CURRENT_USER,
                    r"SOFTWARE\Native Instruments",
                    winreg.KEY_WOW64_64KEY,
                )

            except KeyError:
                pass

        to_be_extracted: Dict[str, IO[bytes]] = {
            name: files[name]
            for name in files
            if name
            not in (
                "uninstall_32bit",
                "kontakt_machine_32bit",
                "kontakt_machine_64bit",
                "kontakt_user_32bit",
                "kontakt_user_64bit",
            )
        }

        for name, file in to_be_extracted.items():

            yield self.get_extractor(
                FileExtractor,
                file,
                pathlib.Path(name),
            )
