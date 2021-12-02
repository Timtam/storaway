import pickle
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import IO, Any, Dict, List, Sequence, Tuple, Type, TypeVar, final

import click

from __version__ import version
from collectors.collector import Collector
from utils.exceptions import WarningException
from utils.platform import Platform, get_current_platform
from utils.warnings import Warnings

T = TypeVar("T", bound=Collector)


@dataclass(init=False)
class ApplicationMetadata:
    collectors_map: Dict[str, int]
    platform: Platform
    storaway_version: str


class Application:

    name: str
    description: str
    platforms: Tuple[Platform, ...]

    _warnings: List[str]
    _warnings_level: Warnings = Warnings.IGNORE

    def __init__(self) -> None:
        self._warnings = []

    def prepare_collectors(self) -> Sequence[Collector]:
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

            self.echo(f"The backup was aborted due to the following error: {str(exc)}")

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
    def report_warning(self, message: str) -> None:
        if self._warnings_level == Warnings.ERROR:
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
                self.echo(f"\t{warning}")
            self._warnings.clear()

    @final
    def set_warnings_level(self, level: Warnings) -> None:
        self._warnings_level = level
