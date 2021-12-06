import pathlib
import zipfile
from typing import IO, List

import click

from .collector import Collector


class FileCollector(Collector):

    path: pathlib.Path

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__()

        self.path = path

    def collect(self, output: IO[bytes]) -> None:

        files: List[pathlib.Path] = []

        def aggregate_files(path: pathlib.Path) -> None:

            nonlocal files

            for file in path.iterdir():

                if file.is_file():
                    files.append(file)
                elif file.is_dir():
                    aggregate_files(file)

        if not self.path.exists():
            self.application.report_warning(
                f"File or directory doesn't exist: {self.path}", critical=True
            )
            return

        self.application.echo("Searching for files...")

        aggregate_files(self.path)

        self.application.echo(f"Found {len(files)} files.")

        zip = zipfile.ZipFile(output, "w", allowZip64=True)

        with click.progressbar(files) as bar:
            for file in bar:
                try:
                    zip.write(file, file.relative_to(self.path))
                except PermissionError:
                    self.application.report_warning(
                        f"Encountered a permission error while reading file {click.format_filename(file)}"
                    )

        zip.close()
