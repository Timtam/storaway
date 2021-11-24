import pathlib
import zipfile
from typing import TYPE_CHECKING, BinaryIO, List

import click

from collectors.collector import Collector

if TYPE_CHECKING:
    from applications.application import Application


class FileCollector(Collector):

    path: pathlib.Path

    def __init__(self, path: pathlib.Path, application: "Application") -> None:
        super().__init__(application=application)

        self.path = path

    def collect(self, output: BinaryIO) -> None:

        files: List[pathlib.Path] = []

        def aggregate_files(path: pathlib.Path) -> None:

            nonlocal files

            for file in path.iterdir():

                if file.is_file():
                    files.append(file)
                elif file.is_dir():
                    aggregate_files(file)

        self.application.echo("Searching for files...")

        aggregate_files(self.path)

        self.application.echo(f"Found {len(files)} files.")

        zip = zipfile.ZipFile(output, "w", allowZip64=True)

        with click.progressbar(files) as bar:
            for file in bar:
                try:
                    zip.write(file, file.relative_to(self.path))
                except PermissionError:
                    self.application.echo(
                        f"Encountered a permission error while reading file {click.format_filename(file)}"
                    )

        zip.close()
