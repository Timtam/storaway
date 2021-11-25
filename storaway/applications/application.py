import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import IO, TYPE_CHECKING, Any, Sequence, Tuple, Type, TypeVar

import click

from collectors.collector import Collector

if TYPE_CHECKING:
    from utils.platform import Platform

T = TypeVar("T", bound=Collector)


class Application:

    name: str
    description: str
    platforms: Tuple["Platform", ...]

    def prepare_collectors(self) -> Sequence[Collector]:
        return []

    def echo(self, message: str, err: bool = False) -> None:
        click.echo(message=f"[{self.name}] {message}", err=err)

    def backup(self, output: IO[bytes]) -> None:

        self.echo("Starting backup")

        collectors = self.prepare_collectors()

        zip = zipfile.ZipFile(output, "w", allowZip64=True)

        for i, collector in enumerate(collectors):

            self.echo(f"Step {i + 1}/{len(collectors)}: Starting...")

            target_file = tempfile.TemporaryFile()

            collector.collect(target_file)

            target_file.seek(0)

            with zip.open(f"{i}", "w", force_zip64=True) as file:
                shutil.copyfileobj(target_file, file)

            target_file.close()

            self.echo(f"Finished step {i + 1}/{len(collectors)}")

        zip.close()

        self.echo("Finished backup")

    def get_backup_file_name(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H-%M-%S") + f"_{self.name}.stor"

    def get_collector(self, collector: Type[T], *args: Any, **kwargs: Any) -> T:
        c = collector(*args, **kwargs)

        c.application = self

        return c
