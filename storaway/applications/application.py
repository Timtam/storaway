import pickle
import shutil
import tempfile
import textwrap
import zipfile
from datetime import datetime
from typing import IO, Any, Dict, List, Sequence, Tuple, Type, TypeVar, final

import click

from __version__ import version
from collectors.collector import Collector
from extractors.extractor import Extractor
from utils.application_metadata import ApplicationMetadata
from utils.exceptions import WarningException
from utils.platform import Platform, get_current_platform
from utils.warnings import Warnings

T = TypeVar("T", bound=Collector)
U = TypeVar("U", bound=Extractor)


class Application:

    name: str
    description: str
    platforms: Tuple[Platform, ...]

    _overwrite: bool
    _warnings: List[str]
    _warnings_level: Warnings = Warnings.IGNORE

    def __init__(self) -> None:
        self._warnings = []
        self._overwrite = False

    def prepare_collectors(self) -> Sequence[Collector]:
        return []

    def prepare_extractors(
        self, collectors: Dict[str, IO[bytes]]
    ) -> Sequence[Extractor]:
        return []

    @final
    def echo(self, message: str, err: bool = False) -> None:
        click.echo(message=f"[{self.name}] {message}", err=err)

    @final
    def backup(self, output: IO[bytes]) -> None:

        self.echo("Starting backup")

        collectors = self.prepare_collectors()

        zip = zipfile.ZipFile(output, "w", allowZip64=True)

        try:

            meta = ApplicationMetadata()

            meta.storaway_version = version
            meta.platform = get_current_platform()
            meta.collectors_map = {}

            for i, collector in enumerate(collectors):

                self.echo(f"Step {i + 1}/{len(collectors)}: Starting...")

                target_file = tempfile.TemporaryFile()

                collector.collect(target_file)

                target_file.seek(0)

                with zip.open(f"{i}", "w", force_zip64=True) as file:
                    shutil.copyfileobj(target_file, file)

                target_file.close()

                meta.collectors_map[collector.name] = i

                self.echo(f"Finished step {i + 1}/{len(collectors)}")

                self.show_warnings()

            with zip.open("metadata", "w") as file:
                file.write(pickle.dumps(meta, pickle.HIGHEST_PROTOCOL))

        except WarningException as exc:

            self.echo(
                textwrap.fill(
                    f"The backup was aborted due to the following error: {str(exc)}"
                )
            )

        finally:

            zip.close()

        self.echo("Finished backup")

    @final
    def get_backup_file_name(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H-%M-%S") + f"_{self.name}.stor"

    @final
    def get_collector(
        self, collector: Type[T], name: str, *args: Any, **kwargs: Any
    ) -> T:
        c = collector(*args, **kwargs)

        c.application = self
        c.name = name

        return c

    @final
    def get_extractor(
        self, extractor: Type[U], input: IO[bytes], *args: Any, **kwargs: Any
    ) -> U:
        e = extractor(*args, **kwargs)

        e.application = self
        e.input = input

        return e

    @final
    def report_warning(self, message: str, critical: bool = False) -> None:
        if self._warnings_level == Warnings.ERROR or critical:
            raise WarningException(message)
        elif self._warnings_level == Warnings.ASK:
            self.echo("The following warning occurred:")
            self.echo(f"\t{message}")
            if click.confirm("Do you want to abort the current process?"):
                raise WarningException(message)
        else:
            self._warnings.append(message)

    @final
    def show_warnings(self) -> None:
        if len(self._warnings) > 0:
            self.echo(f"The following {len(self._warnings)} warning(s) occurred:")
            for warning in self._warnings:
                self.echo(textwrap.fill(f"\t{warning}"))
            self._warnings.clear()

    @final
    def set_warnings_level(self, level: Warnings) -> None:
        self._warnings_level = level

    @final
    def restore(self, input: IO[bytes]) -> None:

        self.echo("Restoring backup")

        if not zipfile.is_zipfile(input):
            self.echo("Error while opening backup file: invalid file format", err=True)
            return

        zip = zipfile.ZipFile(input, "r", allowZip64=True)

        meta: ApplicationMetadata = pickle.loads(zip.read("metadata"))

        files: Dict[str, IO[bytes]] = {}

        for name, index in meta.collectors_map.items():
            files[name] = zip.open(f"{index}", "r")

        try:

            extractors = self.prepare_extractors(files)

            for i, extractor in enumerate(extractors):

                self.echo(f"Step {i + 1}/{len(extractors)}: Starting...")

                extractor.extract()

                self.echo(f"Finished step {i + 1}/{len(extractors)}")

                self.show_warnings()

        except WarningException as exc:

            self.echo(
                textwrap.fill(
                    f"The restoration was aborted due to the following error: {str(exc)}"
                )
            )

        finally:

            for name, file in files.items():
                file.close()

            zip.close()

        self.echo("Finished restoration")

    def set_overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite

    def get_overwrite(self) -> bool:
        return self._overwrite
